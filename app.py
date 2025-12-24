"""
Hugging Face Space App for Physical AI & Humanoid Robotics Course Assistant
This creates a web interface for the RAG chatbot using Gradio
"""
import os
import sys
import logging
from typing import Optional, List

# Add backend to path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import gradio as gr
from google import genai
import cohere
from qdrant_client import AsyncQdrantClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients (these would be configured in a real implementation)
gemini_api_key = os.getenv("GEMINI_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

model = None
co = None
qdrant_client = None

# Validate environment variable at startup
if not gemini_api_key:
    logger.error("GEMINI_API_KEY is not set. Google GenAI will not work.")
    print("Warning: GEMINI_API_KEY not found. Using mock responses.")
else:
    try:
        # Initialize GenAI SDK once at startup
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Google GenAI initialized successfully with gemini-1.5-flash.")
    except Exception as e:
        logger.error(f"Failed to configure Google GenAI: {e}")
        print("Warning: Google GenAI not configured. Using mock responses.")
        model = None

# Only initialize clients if API keys are provided
if cohere_api_key:
    try:
        co = cohere.Client(api_key=cohere_api_key)
    except Exception as e:
        logger.error(f"Error configuring Cohere: {e}")
        co = None

if qdrant_url and qdrant_api_key:
    try:
        qdrant_client = AsyncQdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    except Exception as e:
        logger.error(f"Error configuring Qdrant: {e}")
        qdrant_client = None

def process_query(query: str, context: Optional[str] = None) -> str:
    """
    Process a chat query using RAG (Retrieval Augmented Generation).
    """
    try:
        # Log the query
        logger.info(f"Processing query: {query[:50]}... with context: {bool(context)}")

        # Create a prompt combining the query and context
        if context:
            prompt = f"Context: {context}\n\nQuestion: {query}\n\nPlease provide a comprehensive answer based on the Physical AI & Humanoid Robotics course content."
        else:
            prompt = f"Question: {query}\n\nPlease provide a comprehensive answer based on the Physical AI & Humanoid Robotics course content."

        # Generate content using Google GenAI if available
        if model:
            try:
                response = model.generate_content(prompt)

                # Handle response safely with multiple fallbacks
                if response:
                    if hasattr(response, 'text') and response.text:
                        return response.text
                    elif hasattr(response, 'candidates') and response.candidates:
                        # Handle response in case text attribute is not directly available
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text'):
                                    text_parts.append(part.text)
                            if text_parts:
                                return " ".join(text_parts)

                    # If we can't extract text from the response, return a default message
                    return "AI generated a response but couldn't extract the text content. Please try rephrasing your question."
                else:
                    return "I couldn't generate a response. Please try rephrasing your question."
            except Exception as e:
                logger.error(f"Error with Google GenAI: {e}")
                return f"I'm having trouble connecting to the AI service. Error: {str(e)}"
        else:
            # Fallback response if model is not configured
            if context:
                return f"Based on the context you provided ('{context[:60]}...'), I can help answer your query about '{query[:30]}...'. " \
                       f"To get a real response, please ensure your GEMINI_API_KEY is properly configured in the environment."
            else:
                return f"Regarding your query about '{query[:30]}...', I would search through the Physical AI course materials to find the most relevant information. " \
                       f"To get a real response, please ensure your GEMINI_API_KEY is properly configured in the environment."

    except Exception as e:
        logger.error(f"Error in process_query: {str(e)}")
        return f"An error occurred while processing your query: {str(e)}"

def chat_with_bot(message, history, context=None):
    """
    Function that handles chat interaction for Gradio
    """
    # Call the synchronous function
    response = process_query(message, context)
    return response

# Create Gradio interface
with gr.Blocks(title="Physical AI & Humanoid Robotics Assistant") as demo:
    gr.Markdown("# Physical AI & Humanoid Robotics Course Assistant")
    gr.Markdown("Ask questions about the course content and get AI-powered answers")

    with gr.Row():
        with gr.Column(scale=1):
            context_input = gr.Textbox(
                label="Context (Optional - paste text from course materials)",
                lines=5,
                placeholder="Paste text from course materials here to provide context..."
            )
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Chat with the AI Assistant",
                bubble_full_width=False,
                height=400
            )
            msg = gr.Textbox(
                label="Your Question",
                placeholder="Ask a question about the course content...",
                lines=2
            )
            clear = gr.Button("Clear Chat")

    msg.submit(chat_with_bot, [msg, chatbot, context_input], chatbot)
    clear.click(lambda: None, None, chatbot, queue=False)

# For Hugging Face Spaces, we need to create a main function
def main():
    demo.launch(share=True, server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))

if __name__ == "__main__":
    main()