import streamlit as st


class Layout:

    def show_header(self):
        """
        Displays the header of the app
        """
        st.markdown(
            """
            <h1 style='text-align: center;'>Red Hat - Summit - InstructLab Demo 🐶</h1>
            <h2 style='text-align: center;'>Red Hat I.T. Internal Knowledge Use Case</h2>
            """,
            unsafe_allow_html=True,
        )

    def show_login_details_missing(self):
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Please config your credentials to start chatting.</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def prompt_form(self):
        """
        Displays the prompt form
        """
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_area(
                "Query:",
                placeholder="Ask a question (e.g. 'Should I keep my code private or make it open source?')...",
                key="input",
                label_visibility="collapsed",
            )
            
            submit_button = st.form_submit_button(label="Run Comparison")

            is_ready = submit_button and user_input
        return is_ready, user_input, submit_button 
    
    def advanced_options(self):
        with st.expander("Advanced Options"):
            show_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
            show_full_doc = st.checkbox("Show parsed contents of the document")
        return show_all_chunks, show_full_doc