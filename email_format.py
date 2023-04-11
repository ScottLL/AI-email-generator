import streamlit as st
from langchain import PromptTemplate
from langchain.llms import OpenAI
import os

template2 = """
    Below is an email that may be poorly worded.
    Your goal is to:
    - Properly format the email
    - Convert the input text to a specified tone
    - Convert the input text to a specified dialect

    Here are some examples different Tones:
    - Formal: We went to Barcelona for the weekend. We have a lot of things to tell you.
    - Informal: Went to Barcelona for the weekend. Lots to tell you.  

    Here are some examples of words in different dialects:
    - American: French Fries, cotton candy, apartment, garbage, cookie, green thumb, parking lot, pants, windshield
    - British: chips, candyfloss, flag, rubbish, biscuit, green fingers, car park, trousers, windscreen

    Example Sentences from each dialect:
    - American: I headed straight for the produce section to grab some fresh vegetables, like bell peppers and zucchini. After that, I made my way to the meat department to pick up some chicken breasts.
    - British: Well, I popped down to the local shop just the other day to pick up a few bits and bobs. As I was perusing the aisles, I noticed that they were fresh out of biscuits, which was a bit of a disappointment, as I do love a good cuppa with a biscuit or two.

    Please start the email with a warm introduction. Add the introduction if you need to.
    
    Below is the email, tone, and dialect:
    TONE: {tone}
    DIALECT: {dialect}
    EMAIL: {email}
    YOUR {dialect} RESPONSE:
"""

def load_LLM(openai_api_key):
    llm = OpenAI(api_key=openai_api_key, temperature=0.5)
    return llm



def email_format(openai_api_key):
    st.markdown ("## :outbox_tray: :red[AI Email Format Generator] ")
    llm = load_LLM(openai_api_key)
    prompt = PromptTemplate(
    input_variables=["tone", "dialect", "email"],
    template= template2
    )
    st.markdown("### Enter your email to Convert")

    col1, col2 = st.columns(2)
    with col1:
        option_tone = st.selectbox("Select the tone of the email", ("Formal", "Informal"))

    with col2:
        option_dialect = st.selectbox("Select the dialect of the email", ("American", "British"))

    def get_text():
        input_text = st.text_area(label="", placeholder="Enter your email here", key="input_text")
        return input_text

    email_input = get_text()

    if st.button("Generate Convert Email"):
        st.markdown("### Your Convert Email")

        if email_input:
            # Generate the response using OpenAI's LLM
            prompt_with_email = prompt.format(tone=option_tone, dialect=option_dialect, email=email_input)
            formatted_email = llm(prompt_with_email)
            st.write(formatted_email)
