import streamlit as st
import requests
import speech_recognition as sr
import re
from PIL import Image
from datetime import datetime
import os
from sqlalchemy import create_engine, text



driver = '{ODBC Driver 17 for SQL Server}'
odbc_str = 'mssql+pyodbc:///?odbc_connect=' \
                'Driver='+driver+ \
                ';Server=tcp:' + SERVER + \
                ';DATABASE=' + DATABASE + \
                ';Uid=' + USERNAME+ \
                ';Pwd=' + PASSWORD + \
                ';TrustServerCertificate=no;Connection Timeout=30;'

db_engine = create_engine(odbc_str)
print("Database connected")

st.set_option('deprecation.showPyplotGlobalUse', False)
html_string = """<style> 
            .stButton{
                position: fixed; 
                margin-left:650px;
                bottom: 120px; 
                background-color: rgb(255, 255, 255);
                z-index: 99
                }
            .stDeployButton{
                visibility: hidden;
            }
            #MainMenu {visibility: hidden;}
                </style>
                """
st.markdown(html_string, unsafe_allow_html=True)

# Initialize speech recognizer
recognizer = sr.Recognizer()

def is_valid_path(path):
    return os.path.exists(path)


def extract_code_from_markdown(md_text):
    """
    Extract Python code from markdown text.

    Parameters:
    - md_text: Markdown text containing the code

    Returns:
    - The extracted Python code
    """
    # Extract code between the delimiters
    code_blocks = re.findall(r"```(python)?(.*?)```", md_text, re.DOTALL)

    # Strip leading and trailing whitespace and join the code blocks
    code = "\n".join([block[1].strip() for block in code_blocks])

    return code


def execute_openai_code(response_text: str):
    """
    Execute the code provided by OpenAI in the app.

    Parameters:
    - response_text: The response text from OpenAI
    - df: DataFrame containing the data
    - query: The user's query
    """

    # Extract code from the response text
    code = extract_code_from_markdown(response_text)
    print('code',code)
    # If there's code in the response, try to execute it
    if code:
        try:
            # Create a folder named "charts" if it doesn't exist
            charts_folder = "charts"
            os.makedirs(charts_folder, exist_ok=True)

            # Append the datetime to the image name
            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_image_path = os.path.join(charts_folder, f"plot_{current_datetime}.png")

            # Append code to save the plot with the dynamic image name
            code += f"""\nlocal_image_path = '{local_image_path}'\nplt.savefig(local_image_path, format='png')"""
            exec(code)
            st.pyplot()

            # Read the saved image in Streamlit and show it
            st.session_state.messages.append({"role": "assistant", "content": local_image_path})
        
        except Exception as e:
            error_message = str(e)
            st.error(
                f"📟 Apologies, failed to execute the code due to the error: {error_message}"
            )
            st.warning(
                """
                📟 Check the error message and the code executed above to investigate further.

                Pro tips:
                - Tweak your prompts to overcome the error 
                - Use the words 'Plot'/ 'Subplot'
                - Use simpler, concise words
                - Remember, I'm specialized in displaying charts not in conveying information about the dataset
            """
            )
    else:
        message_placeholder = st.empty()
        message_placeholder.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})


# Define a function for getting a response from the AI assistant
def reponse_fun(prompt=''):
    # Make a POST request to your FastAPI endpoint
    url = "http://localhost:8000/ask"
    question = prompt
    response = requests.post(url, json={"question": question, "user_id": user_id})

    if response.status_code == 200:
        data = response.json()
        full_response = data["response"]
        
    else:
        full_response = "Failed to get a response."
    
    return full_response


# Define a function for voice input processing
def run_voice_input():
    with sr.Microphone() as source:    
        recognizer.adjust_for_ambient_noise(source)
        voice_message = st.empty()
        voice_message.write("Listening for voice input...")
        audio_data = recognizer.listen(source)
        # Clear the status message after recording
        voice_message.empty()

        try:
            # Convert voice input to text
            user_input = recognizer.recognize_google(audio_data)
            return user_input  # Return the voice input as the result

        except sr.UnknownValueError:
            st.text("Sorry, I couldn't understand the audio.")
        except sr.RequestError as e:
            st.text(f"Could not request results from Google Speech Recognition service; {e}")

# Define a flag to track authentication status in session_state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Extract user ID from the URL
query_params = st.experimental_get_query_params()
user_id = query_params.get("user_id", [None])[0]

# Check if the user is authenticated
if not st.session_state.authenticated:
    if user_id is not None:
        try:
            user_id = int(user_id)

            # Perform authentication by checking if user_id is in the database
            with db_engine.connect() as connection:
                query = text("SELECT COUNT(*) FROM Employee_Master WHERE Emp_Id = :user_id")
                result = connection.execute(query, {"user_id": user_id})
                count = result.scalar()

            if count == 0:
                st.error("Unauthorized access. You are not allowed to access this chatbot.")
                st.stop()
            # Update the authenticated flag in session_state
            st.session_state.authenticated = True
        except ValueError:
            st.error("Invalid user ID provided in the URL.")
            st.stop()
    else:
        # If user_id is not provided in the URL, deny access
        st.error("Unauthorized access. Please provide a valid user_id in the URL.\nFor Example: http://localhost:8501/?user_id=1111111")
        st.stop()

st.title('Ma_Live Chatbot')
st.markdown(' ')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # print(type(message["content"]))
        # st.markdown(message["content"])
        try:
            if is_valid_path(message["content"]):
                # It's a PIL image
                image = Image.open(message["content"])   # mention the image directory
                st.image(image, caption="Assistant's Image Response", use_column_width=True)
            else:
                st.markdown(message["content"])
        except:
            st.markdown(message["content"])        

if len(st.session_state.messages) == 0:
        # Add initial message
        role = "assistant"
        content = "Hi, How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": content})

        with st.chat_message(role):
            st.markdown(content)


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    # # This code is for adding an image to the chat icon or avatar
    # # for avatar
    # with st.chat_message("user",avatar="👤"):
    # # for image
    # with st.chat_message("user",avatar=st.image(image, width=32)):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Generating response..."):  # Show loading spinner
        full_response = reponse_fun(prompt)

    # Hide the spinner and display the response
    st.spinner()
    with st.chat_message("assistant"):
        execute_openai_code(full_response)

    # st.session_state.messages.append({"role": "assistant", "content": full_response})
    

if st.button("🎙️", key="voice_input_button"):
    voice_input = run_voice_input()
    print(voice_input)
    prompt = voice_input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Generating response..."):  # Show loading spinner
        full_response = reponse_fun(prompt)

    # Hide the spinner and display the response
    st.spinner()
    with st.chat_message("assistant"):
        execute_openai_code(full_response)