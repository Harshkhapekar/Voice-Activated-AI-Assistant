import google.generativeai as genai 

# Set up the API key
genai.configure(api_key="AIzaSyBWkt5ZMXdRf79jC-PSLcBMAhQQNK6zVxQ")

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-pro")

# Define messages (Gemini does not use roles like OpenAI)
prompt = "You are a virtual assistant named Jarvis skilled in general tasks like Alexa and Google Assistant.\n\nWhat is coding?"

# Generate response
response = model.generate_content(prompt)

# Print the response
print(response.text)