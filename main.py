import google.genai as genai
from dotenv import load_dotenv
import os
from ticketBooking_tools import create_ticket_booking_request,get_travel_to_countries,get_booking_details
import gradio as gr
import pyttsx3
import requests
import threading
from auth import auth


# Load environment variables from .env file
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")

client = genai.Client(api_key=google_api_key)

# System prompt defining the AI's persona and capabilities
SYSTEM_PROMPT = (
    "You are a friendly and highly capable flight and hotel booking assistant. "
    "Your goal is to help users book tickets by gathering necessary information and using available tools. "
    "Always start by introducing yourself briefly."
)

# Available tools
AVAILABLE_TOOLS = {
    "create_ticket_booking_request": create_ticket_booking_request,
    "get_travel_to_countries": get_travel_to_countries,
    "get_booking_details": get_booking_details
}

def speak_text(text):
    engine = pyttsx3.init()

    """Speaks the given text."""
    engine.say(text)
    engine.runAndWait()

def speak_async(response_text):
    """Starts speech synthesis in a separate thread to prevent blocking."""
    if response_text:
        thread = threading.Thread(target=speak_text, args=(response_text,))
        thread.daemon = True  # Ensure the thread terminates once execution is complete
        thread.start()
    else:
        print("Error: Response text is empty")

def chat(user_message, history):
    # Construct messages for the API call from Gradio's history
    api_messages = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}] # Start with system prompt
    # Add model's initial response to system prompt (simulated for history consistency)
    if not history: # First turn after system prompt
        api_messages.append({"role": "model", "parts": [{"text": "Hello! I'm your booking assistant. How can I help you today?"}]})

    for user_msg, model_msg in history:
        api_messages.append({"role": "user", "parts": [{"text": user_msg}]})
        if model_msg: # Ensure model_msg is not None
            api_messages.append({"role": "model", "parts": [{"text": model_msg}]})
    
    api_messages.append({"role": "user", "parts": [{"text": user_message}]})

    # First API call to get model's response (might be text or a function call)
    try:
        # Define the tool schema properly
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=api_messages,
            config=genai.types.GenerateContentConfig(
                temperature=0.7, # Slightly higher for more natural interaction
                tools=[create_ticket_booking_request,get_travel_to_countries,get_booking_details]
            )
        )
        # Check for function call
        candidate = response.candidates[0]
        if candidate.content.parts and hasattr(candidate.content.parts[0], 'function_call') and candidate.content.parts[0].function_call:
            function_call = candidate.content.parts[0].function_call
            tool_name = function_call.name
            tool_args = {key: value for key, value in function_call.args.items()}

            print(f"Tool call requested: {tool_name} with args: {tool_args}")

            if tool_name in AVAILABLE_TOOLS:
                tool_function = AVAILABLE_TOOLS[tool_name]
                # Execute the tool function
                api_tool_response = tool_function(**tool_args) # This is a requests.Response object
                # Process the requests.Response into a serializable format for the LLM
                tool_response_content = {
                    "status_code": api_tool_response.status_code,
                    "body": None
                }
                try:
                    tool_response_content["body"] = api_tool_response
                except requests.exceptions.JSONDecodeError:
                    print(f"Tool response: {tool_response_content}")

                # Send the tool's response back to the model
                api_messages.append(candidate.content) # Add model's turn that included the function call
                api_messages.append({
                    "role": "tool", # Use "tool" role for function responses
                    "parts": [genai.types.FunctionResponse(name=tool_name, response=tool_response_content)]
                })

                # Get final response from model after tool execution
                response = client.models.generate_content(model='gemini-1.5-flash', contents=api_messages)
                speak_async(response.text)
                return response.text
            else:
                return f"Error: Tool '{tool_name}' not found."
        else:
            # No function call, just return the text
            speak_async(response.text)
            return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I encountered an error. Please try again."


gr.ChatInterface(chat).launch(auth=auth)