import requests
import json
import os

def get_openai_response(user_content, model="gpt-4o-mini", max_tokens=50, temperature=0.7):
    """
    Fetch a response from OpenAI's Chat Completion API based on user input.

    Args:
        user_content (str): The user's input prompt.
        model (str): The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4").
        max_tokens (int): The maximum number of tokens for the response.
        temperature (float): Sampling temperature (0 to 1).

    Returns:
        str: The content of the response if successful.
        None: If the API request fails.
    """
    # Load your OpenAI API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key not found.")
        return None

    # API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Request payload with only the user's content
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": user_content}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Debug response status and content
    if response.status_code == 200:
        # Parse and return the response content
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    else:
        # Print error details for debugging
        print(f"Error {response.status_code}: {response.text}")
        return None
