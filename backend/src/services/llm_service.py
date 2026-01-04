import os
from groq import Groq

class LLMService:
    def __init__(self):
        # Sirf environment variable use karein
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            # Error throw karein taaki pata chale key missing hai
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        
        self.client = Groq(api_key=self.api_key)

    def generate_response(self, query: str, context: str) -> str:
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer in English:"
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"LLM Error: {str(e)}"