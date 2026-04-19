from langchain_core.embeddings import Embeddings

class EmbeddingService:

    def __init__(self, model: Embeddings):
        self.model = model

    def get_embedding(self) -> Embeddings:
        return self.model