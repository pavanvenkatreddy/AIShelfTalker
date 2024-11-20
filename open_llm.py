import os
import openai

# Set your OpenAI API key
openai.api_key = os.getenv("-key-")  # Ensure the API key environment variable is set correctly

try:
    # Create a chat completion targeting gpt-4-mini
    response = openai.ChatCompletion.create(
        model="gpt-4-mini",  # Use the exact model name you're allowed to access
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        temperature=0.7,  # Optional: Adjust temperature for creativity
    )

    # Print the result
    print("Chat Completion Response:")
    print(response["choices"][0]["message"]["content"])

except Exception as e:
    print(f"Error: {e}")
