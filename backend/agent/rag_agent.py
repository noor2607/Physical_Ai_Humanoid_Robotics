from agent.tools import retrieve_context
from core.config import settings
import os

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or getattr(settings, 'OPENROUTER_API_KEY', None)
if not OPENROUTER_API_KEY:
    # Use a default key if none is provided (this should be replaced with proper configuration)
    OPENROUTER_API_KEY = "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"

MODEL = "mistralai/mistral-7b-instruct"  # Correct OpenRouter model name

SYSTEM_PROMPT = """
You are a textbook assistant for the Physical AI & Humanoid Robotics course.
Answer using ONLY the provided context from the course materials.
If the answer is not in the provided context, say: "I don't know based on the textbook."
"""

class RAGAgent:
    def answer(self, question: str, selected_text: str | None = None):
        # Retrieve context from local Qdrant database
        print(f"DEBUG: Searching for question: {question}")  # Debug print
        context_chunks = retrieve_context(question)
        print(f"DEBUG: Found {len(context_chunks)} context chunks")  # Debug print

        if selected_text:
            context_chunks.insert(0, selected_text)

        if not context_chunks:
            # No context found in local database
            print("DEBUG: No context chunks found")  # Debug print
            return "I don't know based on the textbook."

        # Limit to top 3 context chunks to reduce processing time
        context_chunks = context_chunks[:3]
        context = "\n\n".join(context_chunks)
        print(f"DEBUG: Context length: {len(context)}")  # Debug print

        try:
            # Initialize OpenAI client with OpenRouter inside the try block to handle auth errors
            from openai import OpenAI
            import time

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )

            # Use the OpenAI client to call OpenRouter with timeout
            import threading
            result = [None]
            exception_occurred = [None]

            def make_request():
                try:
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT.strip()},
                            {"role": "user", "content": f"Context from course materials:\n{context}\n\nQuestion: {question}\n\nPlease provide a concise answer based on the context from the course materials:"}
                        ],
                        temperature=0.1,
                        max_tokens=500,
                    )
                    result[0] = response.choices[0].message.content
                except Exception as e:
                    exception_occurred[0] = e

            # Start the request in a thread with timeout
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            thread.join(timeout=10)  # 10 second timeout

            if thread.is_alive():
                # Request timed out
                print("OpenRouter API call timed out")  # Debug print
                # If OpenRouter times out, return the context that was found as fallback
                context_preview = context[:500] + "..." if len(context) > 500 else context
                return f"Retrieved context from course materials: {context_preview}"
            elif exception_occurred[0]:
                # Exception occurred during the call
                print(f"OpenRouter API exception: {str(exception_occurred[0])}")  # Debug print
                # If OpenRouter fails, return the context that was found as fallback
                context_preview = context[:500] + "..." if len(context) > 500 else context
                return f"Retrieved context from course materials: {context_preview}"
            else:
                # Success
                return result[0]

        except Exception as e:
            print(f"OpenRouter API exception: {str(e)}")  # Debug print
            # If OpenRouter fails, return the context that was found as fallback
            context_preview = context[:500] + "..." if len(context) > 500 else context
            return f"Retrieved context from course materials: {context_preview}"
