import streamlit as st
from langchain import PromptTemplate
from langchain.llms import OpenAI
import os
import openai

from email_generator import email_generator, load_LLM
from email_format import email_format
from pdf_gpt import pdf_gpt
from txt_gpt import text_gpt

def empty():
    st.write("Please select a function from the sidebar")


st.set_page_config(page_title="AI Application", page_icon="robot_face",
                   layout="centered", initial_sidebar_state="auto")

st.title ("AI Application :robot_face:" )


content_loaded = False
if "OPENAI_API_KEY" not in os.environ:
    st.markdown("### Input your OpenAI API Key here")
    api_key = st.text_input(label = "", placeholder = "Enter your API Key here", key = "API_input_text")

    if st.button("Load API Key") and api_key.strip() != "":
        os.environ["OPENAI_API_KEY"] = api_key.strip()
        st.success("API Key loaded successfully.")
        content_loaded = True
else:
    content_loaded = True

if content_loaded:
    st.sidebar.title("Functions")

    st.sidebar.markdown("#### Email Functions")
    email_menu_options = ["None", "Generate Emails", "Email Format"]
    email_choice = st.sidebar.radio("", email_menu_options, key="email", index=0)

    st.sidebar.markdown("#### GPT Question")
    gpt_menu_options = ["None", "PDF input", "txt input"]
    gpt_choice = st.sidebar.radio("", gpt_menu_options, key="gpt", index=0)

    if email_choice != "None" and gpt_choice != "None":
        st.sidebar.warning("Please choose only one function.")
        email_choice = "None"
        gpt_choice = "None"

    if email_choice == "Generate Emails":
        llm = load_LLM(os.environ.get("OPENAI_API_KEY"))
        email_generator()
    elif email_choice == "Email Format":
        llm = load_LLM(os.environ.get("OPENAI_API_KEY"))
        email_format()
    elif gpt_choice == "PDF input":
        pdf_gpt()
    elif gpt_choice == "txt input":
        text_gpt()
    else:
        empty()
    
    # menu_options = ["PDF input", "txt input"]
    # choice = st.sidebar.radio("GPT Questions", menu_options)
    

    
    