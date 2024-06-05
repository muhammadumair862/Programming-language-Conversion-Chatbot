from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import pandas as pd
import os

# Setting up the api key
import environ

env = environ.Env()
environ.Env.read_env()

os.environ["OPENAI_API_KEY"] = env("apikey")


def create_agent(filepath: str = "sqlite:///ITSM_DB.db"):
    """
    Create an agent that can access and use a large language model (LLM).

    Args:
        filename: The path to the database file that contains the data.

    Returns:
        An agent that can access and use the LLM.
    """
    # Create a SQL database object.
    db = SQLDatabase.from_uri(filepath)

    # Create an OpenAI object.
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

    return agent_executor


def get_response(agent, input_text: str):
    """
    Get a response from the agent given an input text.

    Args:
        agent: The agent that can access and use the LLM.
        input_text: The input text to the agent.

    Returns:
        The response from the agent.
    """
    prompt = (
        """
            For the following query, if it requires drawing a table, reply as follows:
            {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

            If the query requires creating a bar chart, reply as follows:
            {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

            If the query requires creating a line chart, reply as follows:
            {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

            There can only be two types of chart, "bar" and "line".

            If it is just asking a question that requires neither, reply as follows:
            {"answer": "answer"}
            Example:
            {"answer": "The title with the highest rating is 'Gilead'"}

            If you do not know the answer, reply as follows:
            {"answer": "I do not know."}

            Return all output as a string.

            All strings in "columns" list and data list, should be in double quotes,

            For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}

            Lets think step by step.

            Below is the query.
            Query: 
            """
        + input_text
    )

    # Run the prompt through the agent
    response = agent.run(prompt)

    # Convert the response to a string
    return response.__str__()


 