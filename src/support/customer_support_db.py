"""
Customer Support Database Manager - Handles SQLite database with vector search for customer support documents.
"""

import os
import sqlite3
import json
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
from openai import AsyncAzureOpenAI

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class SupportDocument:
    """Data class for customer support documents."""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    priority: str
    last_updated: str
    embedding: Optional[np.ndarray] = None


class CustomerSupportDB:
    """Customer Support Database Manager with vector search capabilities."""
    
    def __init__(self, db_path: str = "data/customer_support.db"):
        """Initialize the customer support database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.openai_client = None
        logger.info(f"🗄️ Initializing Customer Support DB: {db_path}")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize OpenAI client for embeddings
        self._init_openai_client()
        
        logger.info("✅ Customer Support DB initialized successfully")
    
    def _init_database(self):
        """Initialize the database schema if it doesn't exist."""
        logger.info("🔧 Initializing database schema...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT NOT NULL,  -- JSON array as string
                    priority TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    embedding BLOB  -- Store as binary numpy array
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON support_documents(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON support_documents(priority)")
            
            conn.commit()
            logger.info("✅ Database schema initialized")
    
    def _init_openai_client(self):
        """Initialize the Azure OpenAI client for embeddings."""
        try:
            endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            if not endpoint:
                raise ValueError("AZURE_AI_FOUNDRY_ENDPOINT environment variable is required")
            
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
            
            logger.info("� Using API key authentication for embeddings")
            self.openai_client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-02-15-preview"
            )
            
            logger.info("✅ Azure OpenAI client initialized for embeddings")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            # Continue without embeddings capability
            self.openai_client = None
    
    async def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for the given text using Azure OpenAI.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            numpy array of the embedding or None if failed
        """
        if not self.openai_client:
            logger.warning("⚠️ OpenAI client not initialized, cannot generate embeddings")
            return None
        
        try:
            deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002")
            
            response = await self.openai_client.embeddings.create(
                model=deployment_name,
                input=text
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            logger.debug(f"📊 Generated embedding with dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding: {e}")
            return None
    
    def _serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serialize numpy array to bytes for storage."""
        return embedding.tobytes()
    
    def _deserialize_embedding(self, data: bytes) -> np.ndarray:
        """Deserialize bytes to numpy array."""
        return np.frombuffer(data, dtype=np.float32)
    
    async def add_document(self, document: SupportDocument) -> bool:
        """Add a support document to the database.
        
        Args:
            document: SupportDocument to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📝 Adding document: {document.title}")
            
            # Generate embedding if not provided
            if document.embedding is None and self.openai_client:
                # Combine title and content for embedding
                text_for_embedding = f"{document.title}\n\n{document.content}"
                document.embedding = await self.get_embedding(text_for_embedding)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                embedding_blob = None
                if document.embedding is not None:
                    embedding_blob = self._serialize_embedding(document.embedding)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO support_documents 
                    (id, title, content, category, tags, priority, last_updated, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    document.id,
                    document.title,
                    document.content,
                    document.category,
                    json.dumps(document.tags),
                    document.priority,
                    document.last_updated,
                    embedding_blob
                ))
                
                conn.commit()
                logger.info(f"✅ Document added successfully: {document.id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add document {document.id}: {e}")
            return False
    
    async def search_documents(
        self, 
        query: str, 
        top_k: int = 5, 
        category_filter: Optional[str] = None,
        priority_filter: Optional[str] = None
    ) -> List[Tuple[SupportDocument, float]]:
        """Search for documents using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            category_filter: Optional category filter
            priority_filter: Optional priority filter
            
        Returns:
            List of tuples (document, similarity_score)
        """
        try:
            logger.info(f"🔍 Searching documents for: '{query[:50]}{'...' if len(query) > 50 else ''}'")
            
            # Generate query embedding
            query_embedding = await self.get_embedding(query)
            if query_embedding is None:
                logger.warning("⚠️ Could not generate query embedding, falling back to text search")
                return await self._text_search(query, top_k, category_filter, priority_filter)
            
            # Retrieve all documents with embeddings
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                sql = "SELECT * FROM support_documents WHERE embedding IS NOT NULL"
                params = []
                
                if category_filter:
                    sql += " AND category = ?"
                    params.append(category_filter)
                
                if priority_filter:
                    sql += " AND priority = ?"
                    params.append(priority_filter)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
            
            if not rows:
                logger.info("📭 No documents found with embeddings")
                return []
            
            # Calculate similarities
            results = []
            for row in rows:
                try:
                    doc_embedding = self._deserialize_embedding(row[7])  # embedding column
                    
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    
                    document = SupportDocument(
                        id=row[0],
                        title=row[1],
                        content=row[2],
                        category=row[3],
                        tags=json.loads(row[4]),
                        priority=row[5],
                        last_updated=row[6],
                        embedding=doc_embedding
                    )
                    
                    results.append((document, similarity))
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process document {row[0]}: {e}")
                    continue
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            top_results = results[:top_k]
            
            logger.info(f"✅ Found {len(top_results)} relevant documents")
            for i, (doc, score) in enumerate(top_results[:3]):  # Log top 3
                logger.info(f"📄 {i+1}. {doc.title} (similarity: {score:.3f})")
            
            return top_results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    async def _text_search(
        self, 
        query: str, 
        top_k: int = 5, 
        category_filter: Optional[str] = None,
        priority_filter: Optional[str] = None
    ) -> List[Tuple[SupportDocument, float]]:
        """Fallback text search when embeddings are not available."""
        try:
            logger.info("🔤 Performing text-based search (fallback)")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                sql = """
                    SELECT * FROM support_documents 
                    WHERE (title LIKE ? OR content LIKE ?)
                """
                params = [f"%{query}%", f"%{query}%"]
                
                if category_filter:
                    sql += " AND category = ?"
                    params.append(category_filter)
                
                if priority_filter:
                    sql += " AND priority = ?"
                    params.append(priority_filter)
                
                sql += " ORDER BY CASE WHEN title LIKE ? THEN 1 ELSE 2 END LIMIT ?"
                params.extend([f"%{query}%", top_k])
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
            
            results = []
            for row in rows:
                document = SupportDocument(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    tags=json.loads(row[4]),
                    priority=row[5],
                    last_updated=row[6]
                )
                
                # Simple relevance score based on query matches
                title_matches = row[1].lower().count(query.lower())
                content_matches = row[2].lower().count(query.lower())
                score = (title_matches * 2 + content_matches) / max(len(query), 1)
                
                results.append((document, score))
            
            logger.info(f"✅ Text search found {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Text search failed: {e}")
            return []
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception:
            return 0.0
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM support_documents")
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            logger.error(f"❌ Failed to get document count: {e}")
            return 0
    
    def get_categories(self) -> List[str]:
        """Get all unique categories in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT category FROM support_documents ORDER BY category")
                categories = [row[0] for row in cursor.fetchall()]
                return categories
        except Exception as e:
            logger.error(f"❌ Failed to get categories: {e}")
            return []
    
    async def populate_sample_data(self):
        """Populate the database with sample customer support documents."""
        logger.info("🌱 Populating database with sample customer support data...")
        
        sample_documents = [
            SupportDocument(
                id="billing-001",
                title="How to Update Your Billing Information",
                content="To update your billing information, navigate to Account Settings > Billing > Payment Methods. Click 'Update Payment Method' and enter your new credit card details. Changes take effect immediately for future billing cycles. If you encounter any issues, please contact our billing support team.",
                category="billing",
                tags=["billing", "payment", "account", "credit-card"],
                priority="medium",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="account-001",
                title="Password Reset Instructions",
                content="If you've forgotten your password, go to the login page and click 'Forgot Password'. Enter your email address and we'll send you a reset link. Check your spam folder if you don't see the email within 5 minutes. The reset link expires after 24 hours for security reasons.",
                category="account",
                tags=["password", "reset", "login", "security"],
                priority="high",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="technical-001",
                title="Application Performance Issues",
                content="If you're experiencing slow loading times or timeouts, try these steps: 1) Clear your browser cache and cookies 2) Disable browser extensions 3) Try a different browser 4) Check your internet connection speed. If issues persist, please provide your browser version and operating system when contacting support.",
                category="technical",
                tags=["performance", "browser", "troubleshooting", "speed"],
                priority="high",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="features-001",
                title="How to Export Your Data",
                content="You can export your data in multiple formats: CSV, JSON, or PDF. Go to Settings > Data Export, select your preferred format and date range. Large exports may take several minutes to process. You'll receive an email notification when your export is ready for download. Downloads expire after 7 days.",
                category="features",
                tags=["export", "data", "download", "backup"],
                priority="low",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="billing-002",
                title="Understanding Your Invoice",
                content="Your monthly invoice includes subscription fees, usage charges, and any applicable taxes. The billing period is shown at the top. Usage charges are calculated based on your plan limits. Taxes are applied according to your billing address. For detailed breakdowns, expand each line item in your invoice.",
                category="billing",
                tags=["invoice", "charges", "taxes", "subscription"],
                priority="medium",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="account-002",
                title="Two-Factor Authentication Setup",
                content="Secure your account with two-factor authentication (2FA). Go to Security Settings > Two-Factor Authentication. You can use an authenticator app like Google Authenticator or receive SMS codes. We recommend using an authenticator app for better security. Save your backup codes in a secure location.",
                category="account",
                tags=["2fa", "security", "authentication", "setup"],
                priority="medium",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="technical-002",
                title="API Rate Limiting Guidelines",
                content="Our API has rate limits to ensure fair usage: 1000 requests per hour for basic plans, 5000 for premium plans. If you exceed the limit, you'll receive a 429 status code. Implement exponential backoff in your applications. Rate limits reset every hour. Contact us for enterprise plans with higher limits.",
                category="technical",
                tags=["api", "rate-limit", "development", "integration"],
                priority="medium",
                last_updated=datetime.now().isoformat()
            ),
            SupportDocument(
                id="features-002",
                title="Collaboration and Sharing Features",
                content="Invite team members by going to Team Settings > Add Members. Set permissions for each member: Viewer, Editor, or Admin. Share individual projects using the Share button - you can create view-only or edit links. Links can be password-protected and set to expire. Track who accessed your shared content in the Activity Log.",
                category="features",
                tags=["collaboration", "sharing", "team", "permissions"],
                priority="low",
                last_updated=datetime.now().isoformat()
            )
        ]
        
        for doc in sample_documents:
            await self.add_document(doc)
        
        logger.info(f"✅ Added {len(sample_documents)} sample documents to the database")
