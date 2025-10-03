import requests
import os
import json

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

def generate_content_from_gemini(prompt: str, system_instruction: str = "") -> str:
    """
    Calls the Gemini API to generate content based on a user prompt.

    Args:
        prompt: The user query to send to the model.
        system_instruction: Optional instruction to guide the model's behavior.

    Returns:
        The generated text content, or an error message.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}], # Can enable Google Search grounding
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }

    headers = {'Content-Type': 'application/json'}

    api_url_with_key = f"{BASE_URL}?key={API_KEY}"

    try:
        print("--- Attempting to connect to Gemini API... ---")

        response = requests.post(api_url_with_key, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raises an exception for 4xx or 5xx status codes

        data = response.json()

        generated_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
        
        if generated_text:
            return generated_text
        else:
            # Handle cases where the API returns a response but no text content
            return f"Error: API response received, but no text content was generated. Response details: {data}"

    except requests.exceptions.RequestException as e:
        # Catch network errors, bad status codes, etc.
        print(f"--- API Call Failed ---")
        return f"API Request Error: Could not connect to the service or encountered a status error: {e}"
    except Exception as e:
        # Catch other unexpected errors
        return f"An unexpected error occurred: {e}"