import streamlit as st
import yaml
import os 
import time 
import random


from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings


from db_build import run_db_build
from src.utils import setup_dbqa

# Import config vars
with open('config/config.yml', 'r', encoding='utf8') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

#SAVED CHATBOTS 
st.session_state.saved_chatbots = os.listdir('vectorstore')

def saved_chatbots_updater():
    st.session_state.saved_chatbots.append(st.session_state.name)


# APP INTERFACE
#SIDEBAR 
st.set_page_config(page_title='DocumentAI', page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.sidebar.title('Document AI')
st.sidebar.divider()

st.sidebar.subheader('Create Chatbot')

chatbot_form = st.sidebar.form("chatbot_form")

uploaded_files = st.sidebar.file_uploader("Choose file/s", accept_multiple_files=True)

llm_option = st.sidebar.selectbox(
    'Select a LLM',
    ('OpenAI-GPT3', 'Meta-Llama2')
    ,key="llm"
)

embedding_option = st.sidebar.selectbox(
    'Select an Embedding Model',
    ('OpenAI/text-embedding-ada-002', 'sentence-transformers/gtr-t5-xl',"sentence-transformers/all-MiniLM-L6-v2")
    ,key="embedding"
)


if ((llm_option == "OpenAI-GPT3") | (embedding_option == "OpenAI/text-embedding-ada-002")):
    openai_api_key = st.sidebar.text_input(
        placeholder="Enter an openai api key..",
        label= "OpenAI API",
        key="openai_api"
    )

chatbot_name = st.sidebar.text_input(label="Chatbot Name",key="name")

created = st.sidebar.button("Create",on_click=saved_chatbots_updater)


#CHAT 

c1,c2 = st.columns([0.7, 0.3],gap='medium')


# CHAT OPTIONS 

c2.subheader('Initiate Chatbot')





chatbot_options = c2.selectbox(
    'Select a chatbot',
    st.session_state.saved_chatbots,
    key='chatbot'

)

temperature = c2.slider('Temperature', 0.0, 1.0 , 0.01,key="temperature")

max_tokens = c2.slider("Maximum length",1,4000,2048,key="max_tokens")

initiated = c2.button("Initiate")


# CHAT INTERFACE

c1.subheader(st.session_state.chatbot)

# Initialize chat hitory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with c1.chat_message(message["role"]):
        c1.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with c1.chat_message("user"):
        c1.markdown(prompt)

    # Display assistant response in chat message container
    with c1.chat_message("assistant"):
        message_placeholder = c1.empty()
        full_response = ""
        assistant_response = random.choice(
            [
                "Hello there! How can I assist you today?",
                "Hi, human! Is there anything I can help you with?",
                "Do you need help?",
            ]
        )
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

#FUNCTIONALITY




if created:

    try:
        
        if not uploaded_files:
            st.warning("Please upload a file")   
            st.stop()

        if not st.session_state.name:
            st.warning("Please provide a name for your chatbot!")
            st.stop()        

        if st.session_state.llm.startswith('OpenAI'):
            if not st.session_state.openai_api:
                st.warning("Please provide an API key or choose an opensource model!")
                st.stop()
            else:
                cfg['MODEL_TYPE'] = "openai"
                cfg['OPENAI_API_KEY'] = st.session_state.openai_api

        else:
            cfg['MODEL_TYPE'] = 'llama'
        

        cfg["DATA_PATH"] = f"data/{st.session_state.name}"
        cfg["DB_FAISS_PATH"] = f"vectorstore/{st.session_state.name}"
        cfg["EMBEDDING_MODEL"] = st.session_state.embedding 

        with open('config/config.yml', 'w', encoding='utf8') as ymlfile:
            ymlfile.write(yaml.dump(cfg))

        
        with st.spinner('Uploading files...'):
            os.makedirs(cfg["DATA_PATH"])
            for file in uploaded_files:
                save_path = os.path.join(cfg["DATA_PATH"], file.name)
                #save_path = cfg["DATA_PATH"]+file.name
                with open(save_path, mode='wb') as f:
                    f.write(file.getvalue())
                    
        st.success('Files succesfully uploaded!')
        
        with st.spinner('Creating chatbot...'):

            run_db_build()
            
            
            chatbot_metadata = {k: v for k, v in st.session_state.items()}
            with open(f"data/cb_metadata/{st.session_state.name}", 'w', encoding='utf8') as chat_metadata:
                chat_metadata.write(yaml.dump(chatbot_metadata))
 
        st.success(f"Chatbot {st.session_state.name} successfully created")
        time.sleep(1)
        st.experimental_rerun()

    except Exception as err:
        st.error(err)

    
if initiated:

    with open(f"data/cb_metadata/{st.session_state.chatbot}", 'r', encoding='utf8') as chat_metadata:
        cbmd = yaml.safe_load(chat_metadata)

    st.write(cbmd['llm'])

    if cbmd['llm'].startswith('OpenAI'):
        cfg['MODEL_TYPE'] = "openai"
        cfg['OPENAI_API_KEY'] = cbmd['openai_api']

    cfg["DB_FAISS_PATH "] = f"vectorstore/{cbmd['name']}"
    cfg["EMBEDDING"] = cbmd['embedding'] 


    with open('config/config.yml', 'w', encoding='utf8') as ymlfile:
        ymlfile.write(yaml.dump(cfg))
    

    

    with st.spinner('Initiating chatbot...'):
        dbqa = setup_dbqa()
    st.success("Successfully initiated")