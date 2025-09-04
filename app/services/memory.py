class Memory:
    def __init__(self):
        self.storage = {}

    def store(self, key: str, value: str):
        self.storage[key] = value

    def retrieve(self, key: str) -> str:
        return self.storage.get(key, "")
