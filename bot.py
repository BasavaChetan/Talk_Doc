import streamlit as st
from dotenv import load_dotenv
from file_upload import upload_to_blob
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import time
from Signup import show_login
import concurrent.futures

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    print(text_chunks)
    embeddings = OpenAIEmbeddings()
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    # st.write(embeddings)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def process_file(file):
    upload_to_blob(file)
    return "File processing complete."

#With Streaming effect 
 
def display_chat_history():
    # Ensure the chat history is in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Traverse and display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_userinput(user_question):
    # Check if the 'conversation' attribute is in session state
    if "conversation" not in st.session_state:
        st.warning("Please upload a document to start chatting.")
        return

    # Add user message to chat history and display immediately
    st.session_state.chat_history.append(
        {"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Process the question and get a response
    response = st.session_state.conversation({'question': user_question})
    
    # Streaming assistant response
    full_response = response['answer']  # Assuming 'answer' key holds the response
    displayed_response = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        for chunk in full_response.split():
            displayed_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(displayed_response + "▌")
        message_placeholder.markdown(displayed_response)

    # Add assistant response to chat history
    st.session_state.chat_history.append(
        {"role": "assistant", "content": displayed_response})
    
    

def show_bot():

    load_dotenv()

    # st.set_page_config(page_title="Bot", page_icon=":books:")
    st.title("Talk_Doc")

    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
  
    # Chat with the bot
    display_chat_history()
    user_question = st.chat_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True,type=['pdf','txt'])
        
        checkDocUploaded= False
        if pdf_docs:
            for uploaded_file in pdf_docs:
                st.write("Filename: ", uploaded_file.name)
                checkDocUploaded= True                 
        
        # Check conditions for disabling the "Process" button
        # 1. Check if processing has been done
        processing_done = "processed" in st.session_state and st.session_state.processed
        # 2. Check if no document is uploaded
        document_uploaded = checkDocUploaded
        # 3. If a document is deleted (covered by no_document_uploaded check)

        disable_button = processing_done or (not(document_uploaded))

        if st.button("Process", disabled= disable_button):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)
                
        if st.button("Logout"):
        # Reset the session state to indicate the user is not logged in
            st.session_state.logged_in = False
        # Rerun the app to show the login interface
            st.rerun()

        if st.button("Save File"):

            result_container = st.empty() # An empty container for displaying the result
            progress_bar = st.progress(0) # Initializing the progress bar with 0%
    
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(process_file, uploaded_file)
                for percent_complete in range(100):
                    time.sleep(0.05)  # Simulating some work with a sleep
                    progress_bar.progress(percent_complete + 1)
                result = future.result()
                
            # Display the result when processing is complete
            result_container.text(result)


            





