#!/usr/bin/env python3
"""
Weather Agent Test Script
Tests the weather agent functionality.
"""

import asyncio
import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.weather_agent import WeatherAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_weather_agent():
    """Test the weather agent with various queries."""
    print("🌤️ Testing Weather Agent...")
    
    try:
        # Initialize the weather agent
        weather_agent = WeatherAgent()
        print("✅ Weather Agent initialized successfully!")
        
        # Test queries
        test_queries = [
            "What's the weather in London?",
            "How's the weather in New York City?",
            "Weather for Paris, France",
            "What's the temperature in Tokyo?",
            "Tell me about the weather in Sydney",
            "What's the weather like?"  # No location specified
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            response = await weather_agent.invoke(query)
            print(f"📝 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            print("-" * 80)
        
        print("\n🎉 Weather Agent test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_weather_agent())
