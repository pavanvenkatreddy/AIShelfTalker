import requests
import json

# Define the URL for your API endpoint
api_url = "http://localhost:11434/api/generate"

# Define the request payload
data = {
    "model": "llama3.2",
    "prompt": "Why is the sky blue? Answer only in 20 words."
}

# Send a POST request to the API with json argument, enabling streaming
with requests.post(api_url, json=data, stream=True) as response:
    if response.status_code == 200:
        try:
            # Initialize an empty response accumulator
            full_response = ""

            # Iterate over each line of the streaming response
            for line in response.iter_lines():
                if line:
                    # Parse the line as JSON
                    chunk = json.loads(line)
                    # Append the "response" field to the full response if available
                    full_response += chunk.get("response", "")
                    # Optionally check if "done" is true to stop early
                    if chunk.get("done", False):
                        break
            
            # Print the accumulated full response
            print("Response:", full_response)
        
        except json.JSONDecodeError:
            print("Error: Response is not valid JSON")
            print("Raw Response:", response.text)
    else:
        print(f"Error {response.status_code}: {response.text}")
