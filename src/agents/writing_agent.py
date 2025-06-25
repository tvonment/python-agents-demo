"""
Writing agent for content creation and editing tasks.
"""
import logging
from semantic_kernel import Kernel

from .base_agent import BaseAgent
from ..plugins.writing_plugins import ContentCreationPlugin, EditingPlugin


logger = logging.getLogger(__name__)


class WritingAgent(BaseAgent):
    """Agent specialized in writing and content creation."""
    
    def __init__(self, name: str = "WritingAgent"):
        instructions = """
        You are a Writing Agent specialized in creating high-quality written content.
        
        Your responsibilities include:
        - Writing articles, reports, and documentation
        - Editing and proofreading content
        - Adapting writing style for different audiences
        - Creating compelling narratives and presentations
        - Ensuring clarity, coherence, and engagement
        
        Always produce well-structured, grammatically correct, and engaging content.
        Adapt your writing style based on the target audience and purpose.
        """
        
        super().__init__(
            name=name,
            instructions=instructions,
            description="Specialized agent for writing and content creation"
        )
    
    def _register_plugins(self, kernel: Kernel) -> None:
        """Register writing-specific plugins."""
        # Add content creation plugin
        content_plugin = ContentCreationPlugin()
        kernel.add_plugin(content_plugin, plugin_name="ContentCreation")
        
        # Add editing plugin
        editing_plugin = EditingPlugin()
        kernel.add_plugin(editing_plugin, plugin_name="Editing")
        
        logger.info(f"Registered plugins for {self.name}")
    
    async def write_article(
        self,
        topic: str,
        audience: str = "general",
        style: str = "informative",
        length: str = "medium"
    ) -> str:
        """Write an article on a specific topic."""
        writing_prompt = f"""
        Write a {length} {style} article on the topic: {topic}
        
        Target audience: {audience}
        
        Please ensure the article includes:
        1. An engaging introduction
        2. Well-structured body with clear sections
        3. Supporting facts and examples
        4. A compelling conclusion
        5. Appropriate tone for the target audience
        
        Make the content informative, engaging, and well-organized.
        """
        
        response = await self.invoke(writing_prompt)
        return response.content
    
    async def edit_content(self, content: str, editing_focus: str = "general") -> str:
        """Edit and improve existing content."""
        editing_prompt = f"""
        Please edit the following content with focus on {editing_focus}:
        
        {content}
        
        Editing guidelines:
        1. Check for grammar and spelling errors
        2. Improve clarity and readability
        3. Enhance flow and structure
        4. Ensure consistency in style and tone
        5. Suggest improvements where needed
        
        Provide the edited version along with a brief summary of changes made.
        """
        
        response = await self.invoke(editing_prompt)
        return response.content
    
    async def create_summary(self, content: str, summary_type: str = "executive") -> str:
        """Create a summary of given content."""
        summary_prompt = f"""
        Create a {summary_type} summary of the following content:
        
        {content}
        
        The summary should:
        1. Capture the main points and key insights
        2. Be concise yet comprehensive
        3. Maintain the original meaning and context
        4. Be appropriate for the intended audience
        
        Present the summary in a clear, well-structured format.
        """
        
        response = await self.invoke(summary_prompt)
        return response.content
