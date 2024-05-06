import os

import streamlit as st

import asyncio
import time

from chat_management.chatbot import Chatbot
from chat_management.chat_history import ChatHistory
from ui_components.layout import Layout
from ui_components.sidebar import Sidebar, Utilities
from config_manager import ConfigManager
from model_services.model_comparison import ModelComparison
from snowflake import SnowflakeGenerator
from vector_db.redis_manager import RedisManager
from model_services.model_factory import ModelFactory

from utils.logger import setup_logging
logger = setup_logging()
# logger.info("Logging is set up.")

# logger.debug("This is a debug message")
# logger.info("Processing something")
# logger.warning("This is a warning message")
# logger.info("Processing something")
# logger.error("This is an error message")
# logger.critical("This is a critical message")


def initialize_default_session_variables():
    """Set default values for session variables."""
    default_values = {
        'ready': False,
        'authentication_status': False,
        'reset_chat': False
    }
    for key, value in default_values.items():
        st.session_state.setdefault(key, value)

# async def manage_responses(history, response_container, prompt_container, model_comparison, model_configs, layout):
#     """Manage the responses and prompts for the chatbot."""
#     is_ready, user_input, submit_button = layout.prompt_form()
#     # Display user_input in a streamlit info block
#     if user_input != "":
#         st.info(f"{user_input}...")
#     if is_ready:
#         model_names = [model.model_name for model in model_configs]
#         logger.info(f"Model names (in manage_responses): {model_names}")
#         try:
#             # Generate a full conversation for the simulation
#             full_conversation = history.get_full_conversation()
#             logger.info(f"Model_names: {model_names}")
#             logger.info(f"Full conversation: {full_conversation}")
#             full_conversation_histories = {}
#             for model in model_configs:
#                 logger.info(f"Model: {model}")
#                 logger.info(f"Model name: {model.model_name}")
#                 logger.info(f"Model type: {model.type}")
#                 logger.info(f"Model endpoint: {model.endpoint}")
#                 logger.info(f"Full conversation: {full_conversation}")
#                 # append full_conversation to full_conversation_histories
#                 full_conversation_histories[model.id] = full_conversation
#             #     model.model_name: full_conversation for model in model_configs
#             # }
#             logger.info(f"Full conversation histories: {full_conversation_histories}")
#             # Now display the full conversation for each model
#             logger.info("Calling display_model_comparison_results...")
#             await ModelComparison.display_model_comparison_results(model_comparison, user_input, full_conversation_histories, model_configs)

#             history.generate_messages(response_container)
#         except Exception as e:
#             st.error(f"Error during model comparisons: {e}")
#             logger.error(f"Error during model comparisons: {e}")
#     if st.session_state["reset_chat"]:
#         history.reset()

async def manage_responses(history, response_container, prompt_container, model_comparison, model_configs, layout):
    """Manage the responses and prompts for the chatbot."""
    is_ready, user_input, submit_button = layout.prompt_form()
    # Display user_input in a streamlit info block
    if user_input != "":
        st.info(f"{user_input}...")
    if is_ready:
        logger.info(f"Model configs (in manage_responses): {model_configs}")
        try:
            # Generate a full conversation for the simulation
            full_conversation = history.get_full_conversation()
            # logger.info(f"Full conversation: {full_conversation}")
            # Convert each message in full_conversation to string if it contains AIMessageChunk objects
            full_conversation_str = ", ".join([str(msg) for msg in full_conversation])
            logger.info(f"Full conversation: {full_conversation_str}")

            full_conversation_histories = {}
            for model in model_configs:
                logger.info(f"Model: {model}")
                logger.info(f"Model ID: {model.id}")
                logger.info(f"Model name: {model.model_name}")
                logger.info(f"Model type: {model.type}")
                logger.info(f"Model endpoint: {model.endpoint}")
                # Append full_conversation to full_conversation_histories using model ID as the key
                full_conversation_histories[model.id] = full_conversation
            logger.info(f"Full conversation histories: {full_conversation_histories}")
            # Now display the full conversation for each model
            logger.info("Calling display_model_comparison_results...")
            await ModelComparison.display_model_comparison_results(model_comparison, user_input, full_conversation_histories, model_configs)

            history.generate_messages(response_container)
        except Exception as e:
            st.error(f"Error during model comparisons: {e}")
            logger.error(f"Error during model comparisons: {e}")
    if st.session_state["reset_chat"]:
        history.reset()

def load_and_validate_config():
    """Load and validate configuration, return configs if valid, otherwise stop the app."""
    configs = ConfigManager.load_config_details()
    if not ConfigManager.validate_configurations(configs):
        st.stop()
    return configs

def initialize_ui(configs):
    """Initialize the UI components and return layout and sidebar."""
    st.set_page_config(layout="wide", page_icon="🐶", page_title="Red Hat - Summit - InstructLab Demo")
    layout = Layout()
    sidebar = Sidebar()
    layout.show_header()
    sidebar.show_logo(configs)
    return layout, sidebar

# async def main_application_logic(configs, layout, sidebar):
#     """Handle the main application logic."""
#     redis_url = RedisManager.build_redis_connection_url(configs['redis'])
#     llm = ModelFactory.create_inference_model(configs['inference_server'])

#     sidebar.show_login(configs)
#     if st.session_state["authentication_status"]:
#         await process_authenticated_user_flow(configs, layout, sidebar, llm, redis_url)

async def main_application_logic(configs, layout, sidebar):
    """Handle the main application logic."""
    redis_url = RedisManager.build_redis_connection_url(configs['redis'])

    # Assuming that you want to initialize all models or a specific model
    model_configs = ConfigManager.get_model_configs()
    models = []
    for config in model_configs:
        logger.debug("Config to be passed to ModelFactory:", config)
        model = ModelFactory.create_inference_model(config)
        models.append(model)

    # Example of using the first model if specific logic is not required
    llm = models[0] if models else None

    sidebar.show_login(configs)
    if st.session_state["authentication_status"]:
        await process_authenticated_user_flow(configs, layout, sidebar, llm, redis_url)


async def process_authenticated_user_flow(configs, layout, sidebar, llm, redis_url):
    """Process the flow for an authenticated user."""
    try:
        pdf, doc_content = Utilities.handle_file_upload()
        if not pdf:
            st.info("Upload a PDF file to get started", icon="👈")
            return None, None
        
        if pdf:
            st.header("GenAI Architecture Comparison Tool")
            sidebar.show_options()
            # count number of architectures in configs
            num_models = len(configs['architectures'])
            model_comparison = ModelComparison(number_of_models=num_models)
            model_configs = model_comparison.collect_model_configs()
            
            Chatbot.initialize_chatbot_if_absent(
                session_state=st.session_state,
                pdf=pdf, 
                llm=llm, 
                redis_url=redis_url,
                history_key="chat_history"
            )

            # success = st.success("Document successfully embedded in vector database. Chatbot initialized successfully.")
            # time.sleep(3) # Wait for 3 seconds
            # success.empty() # Clear the alert
            st.session_state["ready"] = True

            history = ChatHistory(history_key="chat_history")
            response_container, prompt_container = st.container(), st.container()
            await manage_responses(history, response_container, prompt_container, model_comparison, model_configs, layout)
    except Exception as e:
        st.error(f"Unexpected error during PDF upload or processing: {e}")
        logger.error(f"Unexpected error during PDF upload or processing: {e}")
        st.stop()

async def main():
    initialize_default_session_variables()
    configs = load_and_validate_config()
    layout, sidebar = initialize_ui(configs)
    await main_application_logic(configs, layout, sidebar)
    sidebar.about()

if __name__ == '__main__':
    asyncio.run(main())

