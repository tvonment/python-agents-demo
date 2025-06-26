"""
Weather Agent - A slim weather information agent using WeatherAPI.com with function calling.
"""

import os
import logging
import requests
from typing import Optional, Annotated
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class WeatherAgent:
    """A slim weather agent that provides current weather information using WeatherAPI.com."""
    
    def __init__(self):
        """Initialize the Weather agent."""
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        if not self.weather_api_key:
            raise ValueError("WEATHER_API_KEY environment variable is required")
        
        self.kernel = self._create_kernel()
        self.kernel.add_plugin(self, plugin_name="weather")
        self.agent = self._create_agent()
    
    def _create_kernel(self) -> Kernel:
        """Create and configure the semantic kernel."""
        kernel = Kernel()
        
        # Azure AI Foundry configuration
        endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        if not all([endpoint, deployment_name, api_key]):
            raise ValueError("Azure OpenAI configuration missing")
        
        chat_completion = AzureChatCompletion(
            endpoint=endpoint,
            deployment_name=deployment_name,
            api_key=api_key
        )
        
        kernel.add_service(chat_completion)
        return kernel
    
    def _create_agent(self) -> ChatCompletionAgent:
        """Create the ChatCompletionAgent."""
        return ChatCompletionAgent(
            kernel=self.kernel,
            name="Weather_Agent",
            instructions="""You are a helpful weather assistant. Use the get_weather function to retrieve current weather data for any city or location. Present the information in a friendly, conversational way. If no city is specified, ask the user to provide one."""
        )
    
    @kernel_function(
        description="Get current weather information for a specific city or location",
        name="get_weather"
    )
    async def get_weather(
        self, 
        city_name: Annotated[str, "The name of the city or location to get weather for"]
    ) -> Annotated[str, "Current weather information formatted as a string"]:
        """Get current weather data for a specific city."""
        try:
            logger.info(f"🌤️ Fetching weather data for: {city_name}")
            
            params = {
                'key': self.weather_api_key,
                'q': city_name,
                'aqi': 'no'
            }
            
            response = requests.get("https://api.weatherapi.com/v1/current.json", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Successfully retrieved weather data for {city_name}")
            
            # Return raw data, let the LLM format it nicely
            location = data['location']
            current = data['current']
            
            return f"""Weather data for {location['name']}, {location['region']}, {location['country']}:
Local time: {location['localtime']}
Temperature: {current['temp_c']}°C ({current['temp_f']}°F)
Feels like: {current['feelslike_c']}°C ({current['feelslike_f']}°F)
Condition: {current['condition']['text']}
Humidity: {current['humidity']}%
Wind: {current['wind_kph']} km/h ({current['wind_mph']} mph) {current['wind_dir']}
Visibility: {current['vis_km']} km ({current['vis_miles']} miles)
Pressure: {current['pressure_mb']} mb ({current['pressure_in']} in)
UV Index: {current['uv']}"""
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Weather API HTTP error for {city_name}: {e}")
            if hasattr(e, 'response') and e.response.status_code == 400:
                return f"Location '{city_name}' not found. Please check the spelling."
            elif hasattr(e, 'response') and e.response.status_code == 401:
                return "Weather API authentication failed."
            else:
                return f"Weather API error: {e}"
        except Exception as e:
            logger.error(f"❌ Unexpected error getting weather for {city_name}: {e}")
            return f"Error getting weather data: {e}"
    
    async def invoke(self, user_message: str, chat_history: Optional[ChatHistory] = None) -> str:
        """Main method to invoke the weather agent.
        
        Args:
            user_message: The user's message
            chat_history: Optional chat history
            
        Returns:
            Weather agent response
        """
        try:
            if chat_history is None:
                chat_history = ChatHistory()
            
            logger.info(f"🌤️ Processing weather request: {user_message}")
            
            # Add user message to chat history
            chat_history.add_user_message(user_message)
            
            # Invoke the agent and collect response from async generator
            response_content = ""
            async for response in self.agent.invoke(chat_history):
                if hasattr(response, 'content'):
                    response_content += str(response.content)
                else:
                    response_content += str(response)
            
            # Add agent response to chat history
            chat_history.add_assistant_message(response_content)
            
            logger.info("✅ Weather request processed successfully")
            return response_content
            
        except Exception as e:
            logger.error(f"❌ Error processing weather request: {e}")
            return f"❌ Sorry, I encountered an error while processing your weather request: {e}"
