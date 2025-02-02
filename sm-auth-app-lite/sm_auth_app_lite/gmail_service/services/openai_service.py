from typing import List
from openai import OpenAI
from ..constants import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for given text using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=OPENAI_EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to create embedding: {str(e)}") 