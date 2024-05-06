import streamlit as st
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.schema import StrOutputParser
from langchain.retrievers.document_compressors.flashrank_rerank import FlashrankRerank
from snowflake import SnowflakeGenerator
from embeddings.doc_embedding import DocEmbedding
from chat_management.chat_history import ChatHistory
import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils.logger import setup_logging
logger = setup_logging()

executor = ThreadPoolExecutor()

class Chatbot:
    def __init__(self, retriever, llm, history_key="chat_history"):
        self.retriever = retriever
        self.llm = llm
        self.history = ChatHistory(history_key)

    @classmethod
    def initialize_chatbot_if_absent(cls, session_state, pdf, llm, redis_url, history_key="chat_history"):
        """Initialize the chatbot if it's not already present in the session state."""
        if 'chatbot' not in session_state:
            index_generator = SnowflakeGenerator(42)
            index_name = str(next(index_generator))
            logger.info("Index Name: " + index_name)
            chatbot = cls.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml", history_key)
            session_state['chatbot'] = chatbot

    @staticmethod
    def setup_chatbot(uploaded_file, llm, redis_url, index_name, schema, chat_history):
        """Sets up the chatbot with the uploaded file, model, and chat history."""
        embeds = DocEmbedding()
        with st.spinner("Initializing the document retriever..."):
            if uploaded_file:
                uploaded_file.seek(0)
                file = uploaded_file.read()
                embeds.create_doc_embedding(file, redis_url, index_name)
                retriever = embeds.get_doc_retriever(redis_url, index_name, schema)
                if retriever:
                    return Chatbot(retriever, llm, chat_history)
                else:
                    st.error("Failed to initialize the document retriever.")
                    return None
            else:
                st.error("Please upload a file to get started.")
                return None

    async def conversational_chat(self, query, configs, config_index):
        logger.info("Starting the conversational chat...")
        if not self.retriever:
            st.error("Document retriever is not initialized.")
            return "No retriever available."
        response = await self.async_invoke_llm(query, configs, config_index)
        return response
    
    async def old_conversational_chat(self, query, config, config_index):

        if not self.retriever:
            st.error("Document retriever is not initialized.")
            return "No retriever available."
        response = await self.async_invoke_llm(query)
        return response

    async def async_invoke_llm(self, query, config, config_index):
        """Invoke the LLM asynchronously."""
        logger.info("Invoking the LLM asynchronously...")
        model_config = config[config_index]

        tab1, tab2, tab3 = st.tabs(["Chat", "Debug", "Details"])

        with tab3:
            st.write("Model Id") # TODO
            st.write("Model Configuration")
            st.write("Endpoint:", model_config.endpoint)
            st.write("Description:", model_config.description)
            st.write("Performing RAG:", model_config.uses_rag)
            st.write("Model Name:", model_config.model_name)

        with tab2:
            # Check if the LLM is initialized
            if self.llm is None:
                st.error("LLM is not initialized.")
                logger.error("LLM is not initialized.")
                return None
            else:
                logger.info("LLM Initialized")

            with st.expander(label="User's Query"):#, expanded=False):
                st.write(query)

            # Retrieve and display documents asynchronously
            docs = await self.retriever.ainvoke(query)
            if docs:
                
                with st.expander(label="Retrieved Documents"):#, expanded=False):
                    st.write(docs)#, expanded=False)

                # Rerank documents using Flashrank
                flashrank_rerank = FlashrankRerank(top_n=3)
                reranked_docs = await flashrank_rerank.acompress_documents(docs, query)

                with st.expander(label="Reranked Documents"):#, expanded=False):
                    st.write(reranked_docs)#, expanded=False)

                # for doc in docs:
                #     st.write(doc if isinstance(doc, str) else doc.page_content)  # Handle both strings and objects with page_content
            
            # Construct the prompt including the query and documents, only after the documents have been retrieved

            # prompt = f"""You are an assistant who only responds with three words - no matter what. Literally only three-word responses. How would you respond to: {query}"""

            prompt = f"""You are a helpful assistant who responds in short concise, but accurate statements. How would you respond to the following user query: \n\n{query}"""
                
            if model_config and model_config.uses_rag:
                st.write("Using RAG model")
                # prompt += f"""\n\nAdditionally, I found the following documents that may be relevant to this inquiry: {[doc if isinstance(doc, str) else doc.page_content for doc in docs]}"""
                
                if model_config and model_config.uses_reranking:
                    docs = reranked_docs

                prompt += "\n\n--- BEGIN DOCS ---n\nAdditionally, I found the following documents that may be relevant to this inquiry:"
                for idx, doc in enumerate(docs, start=1):
                    doc_content = doc if isinstance(doc, str) else doc.page_content
                    prompt += f"\n\n{idx}:\n{doc_content}"
                prompt += "\n\n--- END DOCS ---\n\n"

            prompt += "\n\nPlease provide a response concisely to the original user query above. You can let the user know if you are not certain of the answer."
            logger.info(f"Full prompt: {prompt}")
            with st.expander(label="Prompt including Query and Documents", expanded=False):
                st.write(prompt)

        with tab1:

            # Stream results and display the output
            # st.markdown(f"### Result Stream")
            output_container = st.empty()
            response_buffer = ""  # Buffer to accumulate responses
            logger.info("Setting up the chain for fetching and processing documents...")
            # Prepare the prompt for the Runnable interface
            runnable_prompt = RunnablePassthrough(lambda _: query) if isinstance(query, str) else RunnablePassthrough(lambda _: str(query))
            
            # Define the chain for fetching and processing documents
            rag_chain_from_docs = (
                RunnablePassthrough.assign(context=lambda x: "\n\n".join(doc.page_content for doc in x['context']))
                | runnable_prompt
                | self.llm
                | StrOutputParser()
            )

            # Setup a parallel runnable to handle the retrieval (context) and the LLM processing (question)
            logger.info("Starting the parallel runnable...")
            rag_chain_with_source = RunnableParallel(
                {"context": self.retriever, "question": runnable_prompt}
            ).assign(answer=rag_chain_from_docs)

            # # # Stream responses from LLM and update the output container continuously
            # # Activate the spinner before starting the streaming process
            # with st.spinner(text=''): #text="Loading... Please wait"):
            #     # Initiate streaming responses from LLM and update the output container continuously
            #     for chunk in self.llm.stream(prompt):
            #         if chunk:
            #             response_buffer += chunk  # Append text to the buffer
            #             output_container.markdown(response_buffer)  # Display updated response in the output container

            response_buffer = ""
            output_container = st.empty()
            logger.info("Starting the streaming process...")
            with st.spinner(text='Loading... Please wait'):
                logger.info("Streaming responses from LLM...")
                logger.info(f"Prompt: {prompt}")
                logger.warn("Before streaming...")
                for chunk in self.llm.stream(prompt):
                    if chunk:
                        response_buffer += chunk.content  # Ensure chunk.content is a string
                        output_container.markdown(response_buffer)

