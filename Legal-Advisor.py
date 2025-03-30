
#///////////////////////////// history /////////////////////////////

import streamlit as st
import os
from firebase_config import db, save_chat_history, get_chat_history
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import time
from PIL import Image
load_dotenv()


st.set_page_config(
    page_title="Legal Salahkar",
    page_icon=r"C:\Users\Aryan\OneDrive\Desktop\Ai Tools(Projects)\CLIMAVOX__4_-removebg-preview.png",  # Path to your favicon file
    layout="wide",  # Optional: Adjust layout if needed
)


st.sidebar.title("Legal Salahkar")
# st.sidebar.image(r"C:\Users\Aryan\OneDrive\Desktop\Ai Tools(Projects)\CLIMAVOX__4_-removebg-preview.png","Legal Salahkar", use_column_width=True)  # Path to your logo image


st.sidebar.markdown("<hr>", unsafe_allow_html=True)

# API Keys
groqApi = st.sidebar.text_input("Enter Your Groq Api")
geminiApi = st.sidebar.text_input("Enter Your Gemini Pro Api")
apiSubmit = st.sidebar.button("Submit Api Keys")

if apiSubmit:
    os.environ["GOOGLE_API_KEY"] = geminiApi
    st.sidebar.success("✅Groq Api Key Submitted")
    st.sidebar.success("✅Gemini Api Key Submitted")


#//////////////////////////// Some changes by me #////////////////////////////
groq_api_key = groqApi

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="Llama3-8b-8192"
    # model_name="Llama-3.1-70b-versatile"
    )    
#//////////////////////////// end of some changes #////////////////////////////

# Prompt template
prompt = ChatPromptTemplate.from_template(
    """
    <b>Hello! 🌟 I'm Legal Salahkar, your personal legal advisor. I’m here to assist you with your legal queries.
    if i ask you question in any language please try to give me answer in that language itself.
    </b>

    Here's the information you need:

    Context:
    {context}

    Your Question:
    {input}

    My Advice:
    """
)


# /////////////////// Vector Embedding of India ///////////////////

def vector_embedding_india():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
        st.session_state.loader = PyPDFDirectoryLoader("./docs1")
        st.session_state.docs = st.session_state.loader.load()

        if not st.session_state.docs:
            st.sidebar.error("No documents found. Please check the PDF directory.")
            return

        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:20])

        if not st.session_state.final_documents:
            st.sidebar.error("No documents were split. Please check the document loading and splitting.")
            return

        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)



# //////////////////////////// india button ////////////////////////////
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
if st.sidebar.button("📚 India Document Embeddings"):
    vector_embedding_india()
    st.sidebar.success("✅Vector Store DB is ready.")
    st.sidebar.success("✅Now You Can Ask The Question.")
    st.sidebar.success("✅Good To Go.")

st.sidebar.markdown("<hr>", unsafe_allow_html=True)



# # Add a button to start a new chat
# if st.sidebar.button("🔄 Start New Chat"):
#     # Clear the session state
#     st.session_state.messages = []
#     st.session_state.selected_session = None
#     st.sidebar.success("New chat session started. 🆕")


# new change
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

if st.sidebar.button("🔄 Start New Chat"):
    # Save current chat history automatically
    if st.session_state.messages:
        # Increment chat counter and create a unique name
        st.session_state.chat_counter += 1
        chat_name = f"chat{st.session_state.chat_counter}"
        save_chat_history(chat_name, st.session_state.messages)
        st.sidebar.success(f"Chat history saved as '{chat_name}'")
    
    # Clear the session state for a new chat
    st.session_state.messages = []
    st.session_state.selected_session = None
    st.sidebar.success("New chat session started. 🆕")
# new change end






st.sidebar.markdown("<hr>", unsafe_allow_html=True)   


import base64
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded_image = base64.b64encode(image.read()).decode()
    
    # Create a CSS style to set the background
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded_image}");
        background-size: cover;
         background-size: {'35rem'} {'35rem'};
        background-position: center;
        background-repeat: no-repeat;        
    }}
    </style>
    """
    
    # Inject CSS with st.markdown
    st.markdown(css, unsafe_allow_html=True)

set_background("nationalemblem3.png")



# Custom CSS for styling
st.markdown("""
    <style>
                        
    /* Change the background color of the sidebar */
    [data-testid="stSidebar"] {
        # background-color: #8B4513; 
        # color:#8b4c20;
        # font-weight: bold;
    }


    .center-text {
        text-align: center;
    }
    .chat-container {
        display: flex;
        flex-direction: column-reverse;
        height: 80vh;
        overflow: auto;
    }
    .chat-message {
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #1e4f7dbd;
        color:black;
        border-radius: 10px;
        padding: 10px;
        max-width: 100%;
        align-self: flex-end;
        word-wrap: break-word;
    }
    .bot-message {
        background-color: #ffecb39c;
        color:black;
        border-radius: 10px;
        padding: 10px;
        max-width: 100%;
        align-self: flex-start;
        word-wrap: break-word;
    }
    .sidebar-footer {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load or initialize chat history
if "selected_session" not in st.session_state:
    st.session_state.selected_session = None

# Sidebar to select or save chat history
with st.sidebar.expander("Chat History Management", expanded=True):
    # Save current chat history
    if st.sidebar.button("Save Current Chat"):
        session_name = st.sidebar.text_input("Session Name")
        if session_name:
            save_chat_history(session_name, st.session_state.messages)
            st.sidebar.success(f"Chat history saved as '{session_name}'")
        else:
            st.sidebar.error("Please enter a session name.")

    # List saved sessions
    
    saved_sessions = [doc.id for doc in db.collection('chat_histories').stream()]
    selected_session = st.sidebar.selectbox("Load Chat History", ["Select a session"] + saved_sessions)

    if selected_session and selected_session != "Select a session":
        st.session_state.messages = get_chat_history(selected_session)
        st.session_state.selected_session = selected_session
        st.sidebar.success(f"Loaded chat history for '{selected_session}'")

# Display chat messages
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        message_class = "user-message" if message["role"] == "user" else "bot-message"
        st.markdown(f'<div class="chat-message {message_class}">{message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar content with centered text
st.sidebar.markdown("<h2 class='center-text'>Developed with ❤️ for GenAI by <a href='https://www.linkedin.com/in/aryan-tiwari-174a50298/' style='text-decoration:none;'>Team Legal Salahkar</a></h2>", unsafe_allow_html=True)



#/////////////////////////////// mic code by aryan ///////////////////////////////
import speech_recognition as sr
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # st.info("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand the audio."
        except sr.RequestError:
            return "Sorry, the service is unavailable."


if st.button("🎤 Speak"):
    user_input = recognize_speech()
    if user_input:
        st.markdown(f'<div class="chat-message user-message">{user_input}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_input})

        if "vectors" in st.session_state and st.session_state.vectors:
            document_chain = create_stuff_documents_chain(llm, prompt)
            retriever = st.session_state.vectors.as_retriever()
            retrieval_chain = create_retrieval_chain(retriever, document_chain)

            try:
                response = retrieval_chain.invoke({'input': user_input})

                if 'answer' in response and response['answer']:
                    st.markdown(f'<div class="chat-message bot-message">{response["answer"]}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "bot", "content": response['answer']})
                else:
                    st.error("No answer found for the given query.")
            except Exception as e:
                st.error(f"Error retrieving answer: {str(e)}")
        else:
            st.error("Vector store is not initialized.")





# Input from user
user_prompt = st.chat_input("Ask To Legal Salahkar")


# Display the question and get the answer if the button is clicked
if user_prompt:
    st.markdown(f'<div class="chat-message user-message">{user_prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    if "vectors" in st.session_state and st.session_state.vectors:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        try:
            response = retrieval_chain.invoke({'input': user_prompt})

            if 'answer' in response and response['answer']:
                st.markdown(f'<div class="chat-message bot-message">{response["answer"]}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "bot", "content": response['answer']})
            else:
                st.error("No answer found for the given query.")
        except Exception as e:
            st.error(f"Error retrieving answer: {str(e)}")
    else:
        st.error("Vector store is not initialized.")
