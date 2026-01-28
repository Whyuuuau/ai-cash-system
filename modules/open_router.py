import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenRouter:
    def __init__(self):
        self.api_key = os.getenv("OPEN_ROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        
        if not self.api_key:
            print("Warning: OPEN_ROUTER_API_KEY not found in environment variables.")

    def create_chat_completion(self, model, messages, temperature=0.7):
        """
        Create a chat completion using OpenRouter API
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://seven-two-hour-cash-system.com", # Optional, for including your app on openrouter.ai rankings.
            "X-Title": "72 Hour Cash System" # Optional. Shows in rankings on openrouter.ai.
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        max_retries = 5
        retry_delay = 5 # seconds
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, headers=headers, json=data)
                
                if response.status_code == 429:
                    print(f"⚠️  Rate limit hit (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                print(f"Error calling OpenRouter API: {e}")
                if hasattr(e.response, 'text') and e.response:
                    print(f"Response text: {e.response.text}")
                
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return None
        return None

# Simple test if run directly
if __name__ == "__main__":
    client = OpenRouter()
    if client.api_key:
        try:
            response = client.create_chat_completion(
                model="deepseek/deepseek-r1-0528:free", # Using a free model for testing
                messages=[{"role": "user", "content": "Hello, are you working?"}]
            )
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("Set OPENROUTER_API_KEY to test.")