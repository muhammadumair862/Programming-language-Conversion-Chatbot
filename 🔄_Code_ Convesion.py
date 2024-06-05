from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import streamlit as st
import os
import environ

env = environ.Env()
environ.Env.read_env()

st.set_page_config(layout="wide")
os.environ["OPENAI_API_KEY"] = env("apikey")

model = ChatOpenAI(model="gpt-3.5-turbo")

# Define a list of supported target languages (feel free to add more)
target_languages = top_30_languages = [
    "Python",    "JavaScript",    "Java",    "C#",
    "C",    "C++",    "TypeScript",    "PHP",
    "Swift",    "Ruby",    "Go",    "Kotlin",
    "Rust",    "R",    "Dart",    "Scala",
    "Perl",    "Objective-C",    "MATLAB",    "Lua",
    "Haskell",    "Elixir",    "Clojure",    "F#",
    "VB.NET",    "Julia",    "Ada",    "Assembly",
    "Scratch",    "VHDL"
]


if st.session_state.get("output_placeholder") is None:
    st.session_state.output_placeholder = ""

# Create a function to convert code (replace this with your actual conversion logic)
def convert_code(input_content, target_language):
    # Define the prompt for the model
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are a helpful assistant. Your task is to converet from given code into the {target_language} Programming language. Use comments additional information if needed. Don't use target programming language in starting of code.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    # Do not add anything from your own.

    # Define the message to be sent to the model
    chain = prompt | model

    response = chain.invoke({"messages": [HumanMessage(content=input_content)]})

    return response.content


def main():
    # Set the title of the app
    st.title("Code Converter App")

    # Create a select box to choose the target language
    target_language = st.selectbox("Select Target Language", target_languages, key="target_language")

    col1, col2 = st.columns(2)

    with col1:
        # Create a text area for input code
        code = st.text_area("Input Code", height=350)
    with col2:
        # Placeholder to display the output code (we'll recreate this later)
        # st.markdown("Output Code", unsafe_allow_html=True, value=st.session_state.output_placeholder, height=250)
        st.text_area("Output Code", height=350, value=str(st.session_state.output_placeholder).replace('```',''), disabled=True)
        # st.text_area("Output Code", height=250, value=st.session_state.output_placeholder)
        # st.markdown('Output<br><div class="st-as st-am st-cx st-b4 st-b5 st-ae st-af st-ag st-cy st-ai st-aj st-b6 st-bb"><code>' + st.session_state.output_placeholder + '</code></div>', unsafe_allow_html=True)

    # Convert the code based on user selection
    if st.button("Convert"):
        converted_code = convert_code(code, target_language)

        # Update the output placeholder
        st.session_state.output_placeholder = converted_code
        st.rerun()

if __name__ == "__main__":
  main()