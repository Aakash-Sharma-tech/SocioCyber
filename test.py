import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyCd7onQA-h_nIwgRYbUADolZ29MMjuhW3U")  # replace with your API key

# User message
user_message = "What is AIML"

# Create model instance
model = genai.GenerativeModel("gemini-pro")

# Generate response
response = model.generate_content(user_message)

# Print response text
print(response.text)
