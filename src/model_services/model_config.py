class ModelConfig:
    """
    Class to store model configuration details.
    """
    def __init__(self, name, description, endpoint, uses_rag, model_name=None, type='ollama', id=None, model_source=None, uses_reranking=False):
        self.id = id
        self.name = name
        self.description = description
        self.endpoint = endpoint
        self.uses_rag = uses_rag
        self.uses_reranking = uses_reranking
        self.model_name = model_name
        self.type = type
        self.model_source = model_source

    def __str__(self):
            return f"ModelConfig(name={self.name}, description={self.description}, endpoint={self.endpoint}, uses_rag={self.uses_rag}, model_name={self.model_name}, type={self.type}), id={self.id}, model_source={self.model_source}, uses_reranking={self.uses_reranking}"
