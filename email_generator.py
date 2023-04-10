import streamlit as st
from langchain import PromptTemplate
from langchain.llms import OpenAI
import os
template1 = """
    Below is an email that I need to write a response with.
    Your goal is to:
    - write a response email to the email input
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

    please write a response email start with a warm introduction. Add the introduction if you need to.
    
    Below is the email, tone, and dialect:
    TONE: {tone}
    DIALECT: {dialect}
    EMAIL: {email}
    YOUR {dialect} RESPONSE:
    
    write an response email to the email input
"""

def load_LLM(openai_api_key):
    llm = OpenAI(api_key=openai_api_key, temperature=0.5)
    return llm



def email_generator():
    st.markdown ("## :black_nib: :blue[AI Email Response Generator] ")
    
    llm = load_LLM(os.environ.get("OPENAI_API_KEY"))
    prompt = PromptTemplate(
    input_variables=["tone", "dialect", "email"],
    template= template1
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

    if st.button("Generate Response Email"):
        st.markdown("### Your Response Email")

        if email_input:
            # Generate the response using OpenAI's LLM
            prompt_with_email = prompt.format(tone=option_tone, dialect=option_dialect, email=email_input)
            formatted_email = llm(prompt_with_email)
            st.write(formatted_email)
