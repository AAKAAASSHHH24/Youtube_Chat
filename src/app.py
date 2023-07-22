"""A Simple chatbot that uses the LangChain and Gradio UI to answer questions about wandb documentation."""
import os
from types import SimpleNamespace

import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space

import wandb
from chains import get_answer, load_chain, load_vector_store
from config import default_config
from ingest import main

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

openai_key = os.getenv("OPENAI_API_KEY")

st.title('🎈 AI YOUTUBE CHAT')

st.write('USE THE SIDE BAR ON TOP LEFT TO INPUT THE YOUTUBE VIDEO YOU WANT TO CHAT WITH')

## generated stores AI generated responses
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["I am AI YOUTUBE CHAT, How may I help you?"]
## past stores User's questions
if 'past' not in st.session_state:
    st.session_state['past'] = ['Hi!']

# Layout of input/response containers
input_container = st.container()
colored_header(label='', description='', color_name='red-30')
response_container = st.container()

# User input
## Function for taking user provided prompt as input
def get_text():
    input_text = st.text_input("You: ", "", key="input")
    return input_text

def ytchat():
    # Sidebar contents
    with st.sidebar:
        st.title('💬 Chat with a youtube video')
        st.header('YOUTUBE VIDEO YOU WANT TO CHAT WITH')
        st.subheader("Your Youtube video link")
        video_url = st.text_input('Enter VIDEO LINK and click Process:')

        if video_url[0:24]=='https://www.youtube.com/':
            video_url=video_url
        else:
            video_url = video_url.split('youtu.be/')[-1]
    
        if st.button("Process"):
            try:
                with st.spinner("Processing"):
                    main(video_url)
            except Exception as e:
                st.image('YouTube-Logo.wine.png')

        st.markdown('''
        ## About
        This app is an LLM-powered chatbot built using:
        - [Streamlit](https://streamlit.io/)
        - [Langchain](https://langchain-langchain.vercel.app/docs/get_started)
        ''')
        st.write('Made with ❤️ by [Akash Rakshit](https://www.linkedin.com/in/akash-rakshit-020761175/)')

    ## Applying the user input box
    with input_container:
        user_input = get_text()
        if not user_input:
            st.warning('Please begin conversation by entering your video related Query')
        else:
            wandb_run = wandb.init(
                            project=default_config.project,
                            entity=default_config.entity,
                            job_type=default_config.job_type,
                            config=default_config,
                        )
            vector_store = load_vector_store(
                    wandb_run=wandb_run, openai_api_key=openai_key
                )
            chain = load_chain(
                    wandb_run=wandb_run, vector_store=vector_store, openai_api_key=openai_key
                )
            history = []
    #if st.button("Start Conversation"):
    ## Conditional display of AI generated responses as a function of user provided prompts
    with response_container:
        if user_input:
            user_input = user_input.lower()
            response = get_answer(
                chain=chain,
                question=user_input,
                chat_history=history,
            )
            history.append((user_input, response))
            st.session_state.past.append(user_input)
            st.session_state.generated.append(response)
            
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
                message(st.session_state["generated"][i], key=str(i))
    #else:
        #st.stop()




if __name__ == '__main__':
    ytchat()