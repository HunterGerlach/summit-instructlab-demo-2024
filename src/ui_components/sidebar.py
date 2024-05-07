import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import tempfile

from chat_management.chatbot import Chatbot
from embeddings.doc_embedding import DocEmbedding
from utils.utilities import Utilities


class Sidebar:
    MODEL_OPTIONS = ["mistral", "Llama-2-7b", "Mistral-7B"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.5
    TEMPERATURE_STEP = 0.01

    def __init__(self):
        # Ensure default values are set at initialization
        if 'temperature' not in st.session_state:
            st.session_state['temperature'] = self.TEMPERATURE_DEFAULT_VALUE
        # Initialize the show_details toggle in session state
        st.session_state.setdefault('show_documents', False)
        st.session_state.setdefault('show_prompt', False)
        st.session_state.setdefault('show_details', False)
        if 'streaming_active' not in st.session_state:
            st.session_state['stop_streaming'] = False

    @staticmethod
    def show_logo(config):
        # image_path = "./img/rhone-" + config['event']['location'] + ".png"
        # image_path = "./img/fedora_avatar.png"
        image_path = "./img/summit.png"
        st.sidebar.image(image_path, width=250)

    @staticmethod
    def about():
        about = st.sidebar.expander("About 🐶", expanded=True)
        sections = [
            "#### The mission of the InstructLab (Large-scale Alignment for chatBots) is to advance Large Language Model (LLM) training through innovative techniques. It employs a taxonomy-based curation and synthetic data generation, enabling the open source community to easily contribute to LLM development.",
            "You can find the original paper [here](https://arxiv.org/html/2403.01081v3)." # https://arxiv.org/abs/2403.01081
        ]
        for section in sections:
            about.write(section)
        
        image_path = "./img/instructlab.png"
        st.sidebar.image(image_path)

    @staticmethod
    def show_login(config):
        # Initialize the authentication_status key in st.session_state
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )
        # name, authentication_status, username = authenticator.login('Login', 'sidebar')
        name, authentication_status, username = authenticator.login(fields={'label': 'Login', 'placement': 'sidebar'})

        # Initialize session state variables
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'name' not in st.session_state:
            st.session_state['name'] = None

        # Rest of your authentication logic...

        # Use session state variables for control flow
        if st.session_state["authentication_status"]:
            authenticator.logout('Logout', 'sidebar')
            # st.write(f'Welcome *{st.session_state["name"]}*')
        elif not st.session_state["authentication_status"]:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
        return name, authentication_status, username

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
            st.rerun()
        st.session_state.setdefault("reset_chat", False)

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=st.session_state['temperature'], 
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature

    def show_options(self):
        # Create a section in the sidebar for options
        with st.sidebar:
            self.reset_chat_button()

            with st.expander("Expert Mode"):
                # self.temperature_slider()
                st.markdown("Coming soon...")

            # with st.expander("Display Options"):
            #     self.display_options_toggle()
            # stop_button = st.button('Stop Streaming')
            # Button to stop all streaming
            # if stop_button:
            #     st.session_state['stop_streaming'] = True


    # def display_options_toggle(self):
    #     """Toggle options for detailed sections in chatbot outputs."""
    #     st.checkbox("Show Retrieved Documents", key='show_documents')
    #     st.checkbox("Show Prompt", key='show_prompt')
    #     st.checkbox("Show Query and Documents", key='show_details')
