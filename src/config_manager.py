import yaml
import os
import streamlit as st
from model_services.model_config import ModelConfig

from utils.logger import setup_logging
logger = setup_logging()

class ConfigManager:
    """ Manages application configuration. """

    @staticmethod
    def load_config_details():
        """ Load configuration details from a YAML file. """
        config_path = os.getenv('CONFIG_PATH', 'config.yaml')
        with open(config_path, 'r') as config_file:
            configurations = yaml.safe_load(config_file)
        return configurations

    @staticmethod
    def get_model_configs():
        """ Retrieve model configurations from the YAML file. """
        configs = ConfigManager.load_config_details()
        if configs and 'architectures' in configs:
            model_configs = [ModelConfig(
                id=arch.get('id'),
                name=arch['name'],
                description=arch['description'],
                endpoint=arch['endpoint'],
                uses_rag=arch['uses_rag'],
                uses_reranking=arch.get('uses_reranking', False),
                model_name=arch.get('model_name', 'default_model_name'),
                model_source=arch.get('model_source', 'default_model_source'),
                type=arch.get('type', 'ollama'))  # Ensure the type is being set correctly
                for arch in configs['architectures']]
            for config in model_configs:
                logger.debug("Created ModelConfig:", config)  # This will use the __str__ method
            return model_configs
        else:
            return [] 

    @staticmethod
    def validate_configurations(configurations):
        """ Validate that the configuration is not empty and return a boolean. """
        is_valid = bool(configurations) and all(key in configurations for key in ["redis", "inference_server"])
        if not is_valid:
            st.error("Configuration details are missing or incomplete.")
        return is_valid