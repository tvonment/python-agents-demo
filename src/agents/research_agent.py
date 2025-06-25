"""
Research agent for gathering information and conducting analysis.
"""
import logging
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function

from .base_agent import BaseAgent
from ..plugins.research_plugins import WebSearchPlugin, DataAnalysisPlugin


logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(self, name: str = "ResearchAgent"):
        instructions = """
        You are a Research Agent specialized in gathering, analyzing, and synthesizing information.
        
        Your responsibilities include:
        - Conducting thorough research on given topics
        - Analyzing data and identifying key insights
        - Providing comprehensive summaries and reports
        - Fact-checking and verifying information sources
        - Identifying trends and patterns in data
        
        Always provide well-sourced, accurate, and comprehensive information.
        When presenting findings, include sources and confidence levels where appropriate.
        """
        
        super().__init__(
            name=name,
            instructions=instructions,
            description="Specialized agent for research and information gathering"
        )
    
    def _register_plugins(self, kernel: Kernel) -> None:
        """Register research-specific plugins."""
        # Add web search plugin
        web_search_plugin = WebSearchPlugin()
        kernel.add_plugin(web_search_plugin, plugin_name="WebSearch")
        
        # Add data analysis plugin
        data_analysis_plugin = DataAnalysisPlugin()
        kernel.add_plugin(data_analysis_plugin, plugin_name="DataAnalysis")
        
        logger.info(f"Registered plugins for {self.name}")
    
    async def conduct_research(self, topic: str, depth: str = "comprehensive") -> str:
        """Conduct research on a specific topic."""
        research_prompt = f"""
        Conduct {depth} research on the following topic: {topic}
        
        Please provide:
        1. A comprehensive overview of the topic
        2. Key facts and statistics
        3. Recent developments and trends
        4. Different perspectives or viewpoints
        5. Reliable sources for further reading
        
        Ensure all information is accurate and well-sourced.
        """
        
        response = await self.invoke(research_prompt)
        return response.content
    
    async def analyze_data(self, data_description: str, analysis_type: str = "general") -> str:
        """Analyze data and provide insights."""
        analysis_prompt = f"""
        Analyze the following data: {data_description}
        
        Provide a {analysis_type} analysis including:
        1. Key patterns and trends
        2. Statistical insights
        3. Correlations and relationships
        4. Potential implications
        5. Recommendations based on findings
        
        Present your analysis in a clear, structured format.
        """
        
        response = await self.invoke(analysis_prompt)
        return response.content
