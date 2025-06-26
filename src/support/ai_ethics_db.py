"""
AI Ethics Document Database Manager - Handles SQLite database with vector search for AI ethics documents.
Processes documents using Azure Document Intelligence and stores content for Q&A.
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
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class AIEthicsDocument:
    """Data class for AI ethics documents."""
    id: str
    filename: str
    title: str
    content: str
    page_number: Optional[int]
    section: str
    last_updated: str
    embedding: Optional[np.ndarray] = None


class AIEthicsDB:
    """AI Ethics Document Database Manager with vector search capabilities."""
    
    def __init__(self, db_path: str = "../data/ai_ethics.db", files_path: str = "../data/files"):
        """Initialize the AI ethics document database manager.
        
        Args:
            db_path: Path to the SQLite database file
            files_path: Path to the directory containing PDF files
        """
        self.db_path = db_path
        self.files_path = files_path
        self.openai_client = None
        self.doc_intelligence_client = None
        
        logger.info(f"🗄️ Initializing AI Ethics DB: {db_path}")
        logger.info(f"📁 Files directory: {files_path}")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize clients
        self._init_openai_client()
        self._init_document_intelligence_client()
        
        logger.info("✅ AI Ethics DB initialized successfully (document processing will happen async)")
    
    def _init_database(self):
        """Initialize the database schema if it doesn't exist."""
        logger.info("🔧 Initializing database schema...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_ethics_documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    page_number INTEGER,
                    section TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    embedding BLOB  -- Store as binary numpy array
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_filename ON ai_ethics_documents(filename)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_section ON ai_ethics_documents(section)")
            
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
            
            logger.info("🔑 Using API key authentication for embeddings")
            self.openai_client = AsyncAzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-02-01"
            )
            logger.info("✅ Azure OpenAI client initialized for embeddings")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")
            raise
    
    def _init_document_intelligence_client(self):
        """Initialize the Azure Document Intelligence client."""
        try:
            endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
            api_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_KEY")
            
            if not endpoint:
                raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT environment variable is required")
            
            if not api_key:
                raise ValueError("AZURE_DOCUMENT_INTELLIGENCE_API_KEY environment variable is required")
            
            logger.info("🔑 Using API key authentication for Document Intelligence")
            self.doc_intelligence_client = DocumentIntelligenceClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(api_key)
            )
            logger.info("✅ Azure Document Intelligence client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Document Intelligence client: {e}")
            raise
    
    def _is_database_empty(self) -> bool:
        """Check if the database contains any documents."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ai_ethics_documents")
            count = cursor.fetchone()[0]
            return count == 0
    
    async def _process_all_documents(self):
        """Process all PDF files in the files directory."""
        if not os.path.exists(self.files_path):
            logger.warning(f"📁 Files directory not found: {self.files_path}")
            return
        
        pdf_files = [f for f in os.listdir(self.files_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"📄 No PDF files found in {self.files_path}")
            return
        
        logger.info(f"📄 Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            file_path = os.path.join(self.files_path, pdf_file)
            logger.info(f"🔍 Processing {pdf_file}...")
            await self._process_document(file_path, pdf_file)
    
    async def _process_document(self, file_path: str, filename: str):
        """Process a single PDF document using Azure Document Intelligence."""
        try:
            logger.info(f"📄 Analyzing document: {filename}")
            
            # Read the file
            with open(file_path, "rb") as f:
                document_content = f.read()
            
            # Analyze document with Document Intelligence
            poller = self.doc_intelligence_client.begin_analyze_document(
                "prebuilt-layout", document_content
            )
            result = poller.result()
            
            # Extract text content by pages
            documents = []
            
            for page_idx, page in enumerate(result.pages):
                # Extract text from the page
                page_text = ""
                if hasattr(page, 'lines') and page.lines:
                    page_text = "\n".join([line.content for line in page.lines])
                
                if page_text.strip():  # Only add if there's actual content
                    # Create document chunks - you might want to split larger pages
                    chunks = self._split_text_into_chunks(page_text, max_chunk_size=1000)
                    
                    for chunk_idx, chunk in enumerate(chunks):
                        doc_id = f"{filename}_page_{page_idx + 1}_chunk_{chunk_idx + 1}"
                        
                        document = AIEthicsDocument(
                            id=doc_id,
                            filename=filename,
                            title=self._extract_title_from_filename(filename),
                            content=chunk,
                            page_number=page_idx + 1,
                            section=f"Page {page_idx + 1}, Section {chunk_idx + 1}",
                            last_updated=datetime.now().isoformat()
                        )
                        documents.append(document)
            
            # Generate embeddings and save to database
            logger.info(f"💾 Saving {len(documents)} document chunks to database")
            for document in documents:
                # Generate embedding
                document.embedding = await self._generate_embedding(document.content)
                # Save to database
                self._save_document(document)
            
            logger.info(f"✅ Successfully processed {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error processing document {filename}: {e}")
            raise
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract a readable title from filename."""
        # Remove extension and replace underscores/hyphens with spaces
        title = os.path.splitext(filename)[0]
        title = title.replace("_", " ").replace("-", " ")
        return title.title()
    
    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into smaller chunks for better processing."""
        # Simple splitting by sentences/paragraphs
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for the given text using Azure OpenAI."""
        try:
            deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-ada-002")
            
            response = await self.openai_client.embeddings.create(
                model=deployment_name,
                input=text
            )
            
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            raise
    
    def _save_document(self, document: AIEthicsDocument):
        """Save a document to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Convert embedding to binary
            embedding_blob = document.embedding.tobytes() if document.embedding is not None else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO ai_ethics_documents 
                (id, filename, title, content, page_number, section, last_updated, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document.id,
                document.filename,
                document.title,
                document.content,
                document.page_number,
                document.section,
                document.last_updated,
                embedding_blob
            ))
            
            conn.commit()
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Tuple[AIEthicsDocument, float]]:
        """Search documents using vector similarity.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of tuples containing (document, similarity_score)
        """
        try:
            # Generate embedding for the query
            query_embedding = await self._generate_embedding(query)
            
            # Get all documents with embeddings
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, filename, title, content, page_number, section, last_updated, embedding
                    FROM ai_ethics_documents 
                    WHERE embedding IS NOT NULL
                """)
                
                results = []
                for row in cursor.fetchall():
                    # Reconstruct document
                    doc = AIEthicsDocument(
                        id=row[0],
                        filename=row[1],
                        title=row[2],
                        content=row[3],
                        page_number=row[4],
                        section=row[5],
                        last_updated=row[6],
                        embedding=np.frombuffer(row[7], dtype=np.float32) if row[7] else None
                    )
                    
                    if doc.embedding is not None:
                        # Calculate cosine similarity
                        similarity = np.dot(query_embedding, doc.embedding) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding)
                        )
                        results.append((doc, float(similarity)))
                
                # Sort by similarity (descending) and return top results
                results.sort(key=lambda x: x[1], reverse=True)
                return results[:limit]
                
        except Exception as e:
            logger.error(f"❌ Error searching documents: {e}")
            return []
    
    def get_all_documents(self) -> List[AIEthicsDocument]:
        """Get all documents from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, title, content, page_number, section, last_updated
                FROM ai_ethics_documents
            """)
            
            documents = []
            for row in cursor.fetchall():
                doc = AIEthicsDocument(
                    id=row[0],
                    filename=row[1],
                    title=row[2],
                    content=row[3],
                    page_number=row[4],
                    section=row[5],
                    last_updated=row[6]
                )
                documents.append(doc)
            
            return documents
    
    async def initialize_documents(self):
        """Initialize documents asynchronously. Call this after creating the instance."""
        if self._is_database_empty():
            logger.info("📄 Database is empty, processing documents...")
            await self._process_all_documents()
        else:
            logger.info("✅ Database already contains documents")
