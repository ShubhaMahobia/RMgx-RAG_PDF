class VectorStore:
    def __init__(self):
        self.vectors = []

    def add_vector(self, vector: list):
        self.vectors.append(vector)

    def get_vectors(self) -> list:
        return self.vectors
