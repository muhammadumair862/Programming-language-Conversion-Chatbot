import openai
from utils import create_agent, get_response
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt


def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"answer": response}

def write_response(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        with st.chat_message("assistant"):
            st.markdown(response_dict["answer"])
            st.session_state.messages.append({"role": "assistant", "content": response_dict["answer"]})


    # Check if the response is a bar chart.
    if "bar" in response_dict:
        data = response_dict["bar"]

        df = pd.DataFrame(data['data'], columns=data['columns'])
        df.set_index(df.columns[0], inplace=True)
        # df.set_index("columns", inplace=True)
        # st.bar_chart(df)
        # Plot the bar chart using matplotlib
        plt.figure(figsize=(10, 6))
        df.plot(kind='bar')
        plt.title("Bar Chart")
        plt.xlabel("X-axis Label")
        plt.ylabel("Y-axis Label")

        # Create a folder named "charts" if it doesn't exist
        charts_folder = "charts"
        os.makedirs(charts_folder, exist_ok=True)

        # Append the datetime to the image name
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(charts_folder, f"plot_{current_datetime}.png")
        plt.savefig(plot_path)
        st.pyplot(plt)

        # Read the saved image in Streamlit and show it
        st.session_state.messages.append({"role": "assistant", "content": plot_path})

    # Check if the response is a line chart.
    if "line" in response_dict:
        data = response_dict["line"]
        df = pd.DataFrame(data['data'], columns=data['columns'])

        df.set_index(df.columns[0], inplace=True)
        # st.line_chart(df)
        # Plot the line chart using matplotlib
        plt.figure(figsize=(10, 6))
        df.plot(kind='line')
        plt.title("Line Chart")
        plt.xlabel("X-axis Label")
        plt.ylabel("Y-axis Label")

        # Create a folder named "charts" if it doesn't exist
        charts_folder = "charts"
        os.makedirs(charts_folder, exist_ok=True)

        # Append the datetime to the image name
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(charts_folder, f"plot_{current_datetime}.png")
        plt.savefig(plot_path)
        st.pyplot(plt)

        # Read the saved image in Streamlit and show it
        st.session_state.messages.append({"role": "assistant", "content": plot_path})

    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)
        # Read the saved image in Streamlit and show it
        st.session_state.messages.append({"role": "assistant", "content": df})

    # Check if the response is a pie chart.
    if "pie" in response_dict:
        data = response_dict["pie"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        
        # Assuming the first column is the label and the second column is the value
        labels = df[df.columns[0]]
        sizes = df[df.columns[1]]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        # Create a folder named "charts" if it doesn't exist
        charts_folder = "charts"
        os.makedirs(charts_folder, exist_ok=True)

        # Append the datetime to the image name
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(charts_folder, f"plot_{current_datetime}.png")
        fig.savefig(plot_path)

        st.pyplot(fig)
        # Read the saved image in Streamlit and show it
        st.session_state.messages.append({"role": "assistant", "content": plot_path})


# st.title("👨‍💻 Chat with your Database")

# query = st.text_area("Insert your query")

# if st.button("Submit Query", type="primary"):
#     # Create an agent from the CSV file.
#     agent = create_agent(filepath="sqlite:///ITSM_DB.db")

#     # Query the agent.
#     response = get_response(agent=agent, input_text=query)

#     # Decode the response.
#     decoded_response = decode_response(response)

#     # Write the response to the Streamlit app.
#     write_response(decoded_response)






import streamlit as st
import re
from PIL import Image
from datetime import datetime
import os


# st.set_option('deprecation.showPyplotGlobalUse', False)
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


def is_valid_path(path):
    return os.path.exists(path)

def greeting_response(question: str):
    # System message to set up the context
    system_message = {"role": "system", 
                      "content": f"""Instructions: 
                                    - You are AI Chatbot. Your goal is to response for basic greetings and simple daily conversation queries.
                                    Example:
                                    Question 1: Hi
                                    Response 1: Hello, How can I help you today?

                                    Question 2: "Good morning. How are you today?"
                                    Response 2: "Good morning. I am doing well, thank you. How about you?"
                                    
                                    Question 3: "Good afternoon. How have you been?"
                                    Response 3: "Good afternoon. I've been well, thank you. And you?"
                                    
                                    Question 4: "Good evening. How's everything going?"
                                    Response 4: "Good evening. Everything is going smoothly, thank you. How are you?"


                                    - In case of anyother question, you should response back "sql". like
                                    Example:

                                    User: How many orders are there?
                                    Bot: sql
                                    User: total sales?
                                    Bot: sql
                                    etc...
                      """}

    # Assistant's message (initially empty)
    assistant_message = {"role": "assistant", "content": ""}

    messages = [system_message, {"role": "user", "content": question}, assistant_message]

    # Use OpenAI's ChatCompletion API to generate an answer
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # You can choose a different model if needed
        messages=messages,
        temperature=0,
    )

    response = response.choices[0].message.content
    # - Login time related details are available in Employee_Master table in FirstLoginDate, LastLoginDate columns.
    # - Employee & client Target related info present in TargetMaster table. 
    if 'sql' in response:
        return False
    
    return response

def execute_openai_code(response_text: str):
    """
    Execute the code provided by OpenAI in the app.

    Parameters:
    - response_text: The response text from OpenAI
    - query: The user's query
    """

    message_placeholder = st.empty()
    message_placeholder.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})


# Define a function for getting a response from the AI assistant
def reponse_fun(query=''):
    response = greeting_response(query)
    if response:
        with st.chat_message("assistant"):
            st.markdown(response)

        # Read the saved image in Streamlit and show it
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        return response

    agent = create_agent(filepath="sqlite:///ITSM_DB.db")

    # Query the agent.
    response = get_response(agent=agent, input_text=query)

    # Decode the response.
    decoded_response = decode_response(response)

    # Write the response to the Streamlit app.
    write_response(decoded_response)
    
    return response


st.title('Chatbot')
st.markdown(' ')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
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
        content = "How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": content})

        with st.chat_message(role):
            st.markdown(content)

prompt = st.chat_input("What is up?")
if prompt:
# if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Generating response..."):  # Show loading spinner
        full_response = reponse_fun(prompt)

    # # Hide the spinner and display the response
    # st.spinner()
    # with st.chat_message("assistant"):
    #     execute_openai_code(full_response)

        

