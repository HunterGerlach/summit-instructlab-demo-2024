import streamlit as st
import threading
from model_services.model_config import ModelConfig
from config_manager import ConfigManager

from langchain_core.messages.ai import AIMessageChunk

from utils.logger import setup_logging
logger = setup_logging()

class ModelComparison:
    """
    Class to manage model comparison operations.
    """
    def __init__(self, number_of_models):
        if not isinstance(number_of_models, int) or number_of_models <= 0:
            raise ValueError("The number of models must be a positive integer")
        self.number_of_models = number_of_models
        self.all_models = ConfigManager.get_model_configs()

    # def display_model_configs(self, model_configs):
    #     cols = st.columns(self.number_of_models)
    #     for i, col in enumerate(cols):
    #         with col:
    #             model_config = model_configs[i]
    #             st.markdown(f"#### Architecture {i+1} Configuration")
    #             st.write("Endpoint:", model_config.endpoint)
    #             st.write("Description:", model_config.description)
    #             st.write("Performing RAG:", model_config.uses_rag)
    #             st.write("Model Name:", model_config.model_name)

    def collect_model_configs(self):
        cols = st.columns(self.number_of_models)
        model_configs = []
        # Use model.id for selection to ensure uniqueness
        model_options = {model.id: model for model in self.all_models}

        if not model_options:  # Check if the model options dictionary is empty
            st.error("No models available to configure.")
            return model_configs

        for i, col in enumerate(cols):
            with col:
                # st.markdown(f"#### Architecture {i+1} Configuration")
                if model_options:  # Check again here for safety
                    option_ids = list(model_options.keys())
                    index = i if i < len(option_ids) else 0  # Ensure the index is within the range
                    selected_id = st.selectbox(
                        "Choose Architecture ID",
                        option_ids,
                        index=index,
                        key=f"model_select_{i}"
                    )
                    selected_model = model_options[selected_id]
                    st.markdown(f"##### {selected_model.name}")  # Display model name in a separate field
                    st.write(selected_model.description)
                    st.write("Model Name: :red[", selected_model.model_name,"]")
                    st.write("Model Source: ", selected_model.model_source)
                    st.write("Performing RAG: ", selected_model.uses_rag, "")
                    st.write("Performing Reranking: ", selected_model.uses_reranking, "")
                    st.write("Endpoint:", selected_model.endpoint)
                    model_configs.append(selected_model)
        return model_configs

    def run_model_comparisons(self, model_configs):
        results = {}
        for model in model_configs:
            if model.uses_rag:
                result = self.run_redis_operations(model)
            else:
                result = f"Result from {model.name} at {model.endpoint}"
            results[model.name] = result
        return results

    def run_redis_operations(self, model):
        return f"Result from {model.name} with Redis-based vector search at {model.endpoint}"

    async def oof_display_results(self, user_input, results, model_configs):
        logger.info("Displaying model comparison results...")
        cols = st.columns(self.number_of_models)
        logger.info(f"No of models: {self.number_of_models}")
        logger.info(f"Results: {results}")
        logger.info(f"Total number of columns: {len(cols)}")
        if len(cols) != len(results):
            logger.error("Mismatch in number of columns and results")
        for model_index, (col, (model_name, messages)) in enumerate(zip(cols, results.items())):
        # for model_index, (col, (model_name, messages)) in enumerate(zip(cols, results.items())):
            logger.info(f"Model Index: {model_index}")
            with col:
                logger.info(f"COLUMN: {col}")
                st.markdown(f"#### Output from {model_name}")

                # Assuming the Chatbot class's conversational_chat method is modified to accept config_index
                with st.chat_message("user"):
                    output = await st.session_state["chatbot"].conversational_chat(user_input, model_configs, model_index)

                # Display each message
                for msg in messages:
                    start_idx = msg.find("content=") + len("content=")
                    message_content = msg[start_idx:].strip("'")
                    st.write(message_content) 
        # for col, (model_name, messages) in zip(cols, results.items()):

    async def display_results(self, user_input, results, model_configs):
        logger.info("Displaying model comparison results...")
        cols = st.columns(self.number_of_models)
        logger.info(f"No of models: {self.number_of_models}")
        logger.info(f"Results: {results}")
        logger.info(f"Total number of columns: {len(cols)}")
        if len(cols) != len(results):
            logger.error("Mismatch in number of columns and results")
        for model_index, (col, (model_name, messages)) in enumerate(zip(cols, results.items())):
        # for model_index, (col, (model_name, messages)) in enumerate(zip(cols, results.items())):
            logger.info(f"Model Index: {model_index}")
            with col:
                logger.info(f"COLUMN: {col}")
                st.markdown(f"#### Output from {model_name}")

                # Assuming the Chatbot class's conversational_chat method is modified to accept config_index
                with st.chat_message("user"):
                    output = await st.session_state["chatbot"].conversational_chat(user_input, model_configs, model_index)

                # Display each message
                for msg in messages:
                    start_idx = msg.find("content=") + len("content=")
                    message_content = msg[start_idx:].strip("'")
                    st.write(message_content) 
        # for col, (model_name, messages) in zip(cols, results.items()):

    async def old_display_results(self, user_input, results, model_configs):
        cols = st.columns(len(results))
        for col, (model_name, messages) in zip(cols, results.items()):
            with col:
                st.markdown(f"### Full Conversation from {model_name}")

                with st.chat_message("user"):
                    output = await st.session_state["chatbot"].conversational_chat(user_input, model_configs, col) #TODO - model_index
                for msg in messages:
                    # Extract the message content after the "content=" part
                    # Assuming each message is a string that starts with "content='...'"

                    # Find the start of the actual content, add len("content=") to get the starting index
                    start_idx = msg.find("content=") + len("content=")
                    # Extract the message, trimming the quotes
                    message_content = msg[start_idx:].strip("'")

                    # Display the message content
                    st.write(message_content)  # You can use st.markdown if you need markdown formatting
                    # st.write_stream(message_content)




        # # Iterate over the columns and results; to use the model index, use enumerate(results.items()) For example:
        # # for model_index, (model_name, messages) in enumerate(results.items()):
        #     with col:
        #         st.markdown(f"### Full Conversation from {model_name}")

        #         with st.chat_message("user"):
        #             output = await st.session_state["chatbot"].conversational_chat(user_input, model_configs, model_index) #TODO - model_index
        #         for msg in messages:
        #             # Extract the message content after the "content=" part
        #             # Assuming each message is a string that starts with "content='...'"

        #             # Find the start of the actual content, add len("content=") to get the starting index
        #             start_idx = msg.find("content=") + len("content=")
        #             # Extract the message, trimming the quotes
        #             message_content = msg[start_idx:].strip("'")

        #             # Display the message content
        #             st.write(message_content)  # You can use st.markdown if you need markdown formatting
        #             # st.write_stream(message_content)

    def run_model_comparisons(model_comparison_tool, model_configs):
        """Run model comparisons and return the results."""
        return model_comparison_tool.run_model_comparisons(model_configs)

    async def display_model_comparison_results(model_comparison_tool, user_input, results, model_configs):
        """Display the results of model comparisons."""
        await model_comparison_tool.display_results(user_input, results, model_configs)
