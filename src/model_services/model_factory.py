# import os
# from langchain_community.llms import HuggingFaceTextGenInference, Ollama

# class ModelFactory:
#     """ Factory class for creating inference models. """

#     @staticmethod
#     def create_inference_model(inference_config):
#         """Create and return an inference model based on the provided configuration."""
#         model_type = inference_config.get("type", "ollama")
#         if model_type == "ollama":
#             return Ollama(model="mixtral") # jefferyb/granite
#         else:
#             return HuggingFaceTextGenInference(
#                 inference_server_url=os.getenv('INFERENCE_SERVER_URL', inference_config["url"]),
#                 max_new_tokens=int(os.getenv('MAX_NEW_TOKENS', '20')),
#                 top_k=int(os.getenv('TOP_K', '3')),
#                 top_p=float(os.getenv('TOP_P', '0.95')),
#                 typical_p=float(os.getenv('TYPICAL_P', '0.95')),
#                 temperature=float(os.getenv('TEMPERATURE', '0.9')),
#                 repetition_penalty=float(os.getenv('REPETITION_PENALTY', '1.01')),
#                 streaming=True,
#                 verbose=False
#             )


# model_factory.py

import os
from langchain_community.llms import HuggingFaceTextGenInference, Ollama
from langchain_openai import OpenAI, ChatOpenAI

from utils.logger import setup_logging
logger = setup_logging()

# Set dummy API key to satisfy the library requirement
OPENAI_API_KEY = "dummy"

class ModelFactory:
    """ Factory class for creating inference models based on specific configurations. """

    @staticmethod
    def create_inference_model(model_config):
        """Create and return an inference model based on the provided configuration."""
        # Assuming model_config is an instance of ModelConfig, not a dictionary
        model_type = model_config.type if hasattr(model_config, 'type') else "ollama"
        logger.debug("Configuration received for model creation:", model_config)  # Debug output

        if model_type == "ollama":
            model_name = model_config.model_name if hasattr(model_config, 'model_name') else "mixtral"
            logger.debug(f"Creating Ollama model with {model_name}...")
            return Ollama(model=model_name)
        elif model_type == "hf":
            # Ensure model_name is defined before use
            model_name = getattr(model_config, 'model_name', 'default_model_name')
            logger.debug(f"Creating HuggingFace model with endpoint {getattr(model_config, 'endpoint', 'http://localhost:8000')}...")
            logger.debug(f"Creating HuggingFace model with {model_name}...")
            return HuggingFaceTextGenInference(
                inference_server_url=getattr(model_config, 'endpoint', "http://localhost:8000"),
                max_new_tokens=int(getattr(model_config, 'max_new_tokens', 20)),
                top_k=int(getattr(model_config, 'top_k', 3)),
                top_p=float(getattr(model_config, 'top_p', 0.95)),
                typical_p=float(getattr(model_config, 'typical_p', 0.95)),
                temperature=float(getattr(model_config, 'temperature', 0.9)),
                repetition_penalty=float(getattr(model_config, 'repetition_penalty', 1.01)),
                streaming=getattr(model_config, 'streaming', True),
                verbose=getattr(model_config, 'verbose', False)
            )
        elif model_type == "instruct":
            model_name = model_config.model_name if hasattr(model_config, 'model_name') else "mixtral"
            # Use LangChain's OpenAI LLM, but with a custom OPENAI_API_BASE value
            os.environ['OPENAI_API_BASE'] = getattr(model_config, 'endpoint', "http://localhost:8000")
            openai_api_key=OPENAI_API_KEY
            return ChatOpenAI(model=model_name, openai_api_key=openai_api_key)
