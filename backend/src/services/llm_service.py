import os
from groq import Groq

class LLMService:
    def __init__(self):
        # Environment variable se key uthana (Recommended)
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            # Agar environment mein na mile toh fallback key yahan de sakte hain
            self.api_key = "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"
        
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