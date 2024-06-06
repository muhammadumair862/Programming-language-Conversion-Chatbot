from fastapi import FastAPI, Request, Form
from pydantic import BaseModel

# Import the required libraries and create the FastAPI app
from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit

from sqlalchemy import create_engine
import uvicorn
import openai

app = FastAPI()

OPENAI_API_KEY  = ""
openai.api_key = OPENAI_API_KEY
# Define a Pydantic model for user questions
class UserQuestion(BaseModel):
    question: str
    user_id: int  # Add a field for user_id

# Define the AI assistant setup
def setup_ai_assistant():
    SERVER = ''
    DATABASE = ''
    USERNAME = ''
    PASSWORD = ''

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
    
    # Create an OpenAI Chat model
    llm = ChatOpenAI(temperature=0,openai_api_key=OPENAI_API_KEY, model='gpt-3.5-turbo-16k')

    database_tables = [
                        "Employee_Master",
                        "Rights",
                        "Emp_Rights",
                        "Client_Master",
                        "SharedClients",
                        "Address_Master",
                        "Contact_Master",
                        "Leaves",
                        "Leave_Details",
                        "OrderSaleMasterData",
                        "LocationMasterData",
                        "TargetMaster",
                        "Incentives",
                        "Product_Details",
                        "Variant_Details",
                        "FocusProducts",
                        "GeneralData",
                        "AuditInventory",
                        "ExpenseData",
                        "ExpenseReportData",
                        "Scheme",
                        "Scheme_Details"
                    ]

    # Create a SQLDatabaseChain
    db = SQLDatabase(db_engine, include_tables=database_tables,sample_rows_in_table_info=2)
    print("Database loaded")

    
    sqldb_agent = create_sql_agent(
                                llm=llm,
                                toolkit=SQLDatabaseToolkit(db=db, llm=llm),
                                verbose=True,
                                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                handle_parsing_errors=True,

                            )

    # # add verbose = True this will print the sql query log
    # sqldb_agent = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    print("Agent created")

    return sqldb_agent

# Create the AI assistant instance
sqldb_agent = setup_ai_assistant()

# Define the endpoint to handle user questions
@app.post("/ask")
async def ask_question(user_question: UserQuestion):
    # Extract the user's question from the request
    question = user_question.question
    emp_id = user_question.user_id

    # # Define the prompt template
    # final_prompt = f"""
    #                 question : {question}
    #                 generate the effecient query and response so it will not acceed the CONTEXT WINDOW ISSUE.
                    
    #                 You should now these abbreviations and their meaning.
    #                 Abbreviation: 
    #                 TNO           --- Total Number Of Order
    #                 TOV           --- Total Order Value
    #                 TNVO        --- Total Number / Value Of Order
    #                 TPO           --- Total Products Order
    #                 TQO           --- Total Quantity Order
    #                 ULOD         --- Unique Product Order Daily
    #                 TULOD       --- Total Product Order Daily
    #                 TNS            --- Total Number Of Sale
    #                 TSV            --- Total Sale Value
    #                 TNVS         --- Total Number / Value Of Sale
    #                 TPS            --- Total Products Sale
    #                 TQS           --- Total Quantity Sale
    #                 ULSD          --- Unique Product Sale Daily
    #                 TULSD         --- Total Product Sale Daily
    #                 VC            --- Total Visit
    #                 POVC          --- Productivity Order Visit


    #                 if sql return no result then return no result found. Currency will be in INR. In final answer never give SQL query.
                    
    #                 If user ask to create chart specifically bar and pie chart then follow below instructions
    #                     Before plotting, ensure the data is ready:
    #                     1. Check if columns that are supposed to be numeric are recognized as such. If not, attempt to convert them.
    #                     2. Handle NaN values by filling with mean or median.
                    
    #                     Use package Pandas, Matplotlib or seaborn and from decimal import Decimal ONLY.
    #                     Provide SINGLE CODE BLOCK with a solution using Pandas, from decimal import Decimal and Matplotlib or seaborn plots in a single figure to address the following query:
                        
    #                     - USE SINGLE CODE BLOCK with a solution. 
    #                     - Do NOT EXPLAIN the code 
    #                     - DO NOT COMMENT the code. 
    #                     - ALWAYS WRAP UP THE CODE IN A SINGLE CODE BLOCK.
    #                     - The code block must start and end with ```
                        
    #                     - Example code format ```code```
                    
    #                     - Colors to use for background and axes of the figure : #F0F0F6
    #                     - Try to use the following color palette for coloring the plots : #8f63ee #ced5ce #a27bf6 #3d3b41
    #                     - Size of figure should be plt.figure(figsize=(8, 6))
    #                     - If Values to large then NOT SHOW in le10 format show in LAKHS or CR

    #                 The code for bar or pie chart is not a Action Input. This is final response. So make sure agent not take it as Action Input.
    #                 - Note : only get data for this employee id = {emp_id} and Make SURE he/she is not able to get anyone else data.
    #                 - PLEASE MAKE SURE EMPLOYEE ID NOT SHOW IN FINAL RESPONSE.
    #                 """

# # Prompt for OpenAI API
# final_prompt = f"""
# You are a helpful chatbot designed specifically for {company_name}. You have access to the {database_name} and can answer questions related to {company_terms} and general greetings.

#  {question}

# **Instructions:**

# - Retrieve and display the login time for the current user from the FirstLoginDate or LastLoginDate column. If both are None, return "No login time found."
# - Use clear and concise language, avoiding technical jargon unless necessary.
# - Tailor responses to the specific needs and culture of {company_name}.
# - Generate efficient query and response within the model's token limit.
# - If SQL returns NULL, return "No result found."
# - Use Pandas, Matplotlib, or Seaborn to create bar or pie charts if requested, following the specified formatting guidelines.
# - Only retrieve data for the employee with ID = {emp_id}. Ensure strict privacy and data protection measures.
# - Do not display the employee ID in the final response.
# - Refer to the following company-specific terms and data sources as needed: {company_terms}, {data_sources}
# """
    
    # System message to set up the context
    system_message = {"role": "system", 
                      "content": f"""Instructions: 
                                    - You are an Ma Live Chatbot. Your goal is to response for basic greetings only. 
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can choose a different model if needed
        messages=messages,
        temperature=0,
    )

    response = response['choices'][0]['message']['content']
    # - Login time related details are available in Employee_Master table in FirstLoginDate, LastLoginDate columns.
    # - Employee & client Target related info present in TargetMaster table. 
    if 'sql' in response: 
        final_prompt = f"""             
                            You have access to the database to answer the user queries from database.
                            - IF USER ASK FOR BAR or PIE CHART. Then first apply query on database and then return the raw result to user.
                            - Return result with small information.
                            question: {question}
    
                            **Instructions:**
                            - Generate efficient query and response that do not exceed the CONTEXT WINDOW ISSUE or token limit.
                            - Only retrieve data for the employee with ID = {emp_id}.
                            - Only use the column names that are available in the database tables.
                            - The currency is INR.
                            
                            You should know these abbreviations and their meaning.
                            **Abbreviation:**
                            TNO           --- Total Number Of Order
                            TOV           --- Total Order Value
                            TNVO        --- Total Number / Value Of Order
                            TPO           --- Total Products Order
                            TQO           --- Total Quantity Order
                            ULOD         --- Unique Product Order Daily
                            TULOD       --- Total Product Order Daily
                            TNS            --- Total Number Of Sale
                            TSV            --- Total Sale Value
                            TNVS         --- Total Number / Value Of Sale
                            TPS            --- Total Products Sale
                            TQS           --- Total Quantity Sale
                            ULSD          --- Unique Product Sale Daily
                            TULSD         --- Total Product Sale Daily
                            VC            --- Total Visit
                            POVC          --- Productivity Order Visit

                        """


        # Call your SQL and OpenAI agents to get the response
        # #### not working with handle_parsing_errors=True
        # response = sqldb_agent.run(final_prompt, handle_parsing_errors=True)
        
        # #### working 
        try:
            response = sqldb_agent.run(final_prompt)
        except Exception as e:
            response = str(e)
            if "Could not parse LLM output:" in response:
                response = response.split("Could not parse LLM output:")[-1]
                response = response.replace("`", "").strip()
            # response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
        
        try:
            a = int(response)
        except:
            # System message to set up the context
            system_message = {"role": "system", 
                            "content": f"""
                                context: {response}
                                Instructions: 
                                **IF USER ASK FOR BAR or PIE CHART Then follow below points:**
                                - Use context data and perform below steps.
                                - Use Pandas, Matplotlib, or Seaborn to create bar or pie charts if requested, following the specified formatting guidelines.
                                - Before plotting, ensure numeric columns are recognized as such.
                                - Handle NaN values by filling with mean or median.
                                - Provide one code block only with a solution using Pandas, Matplotlib, and Decimal.
                                - Example code format ```code```
                                - Colors for background and axes: #F0F0F6
                                - Color palette for plots: #8f63ee #ced5ce #a27bf6 #3d3b41
                                - Size of figure: plt.figure(figsize=(8, 6))
                                - If values are too large, show in LAKHS or CR.

                            **IF USER NOT ASK FOR BAR or PIE CHART Then follow below points:**
                            - If context response is only number then return the number as response.
                            - Please retrn context response without employee id in your response.
                            """}
            # Assistant's message (initially empty)
            messages = [system_message, {"role": "user", "content": question}, assistant_message]
            # Use OpenAI's ChatCompletion API to generate an answer
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # You can choose a different model if needed
                messages=messages,
                temperature=0,
            )
            response = response['choices'][0]['message']['content']
    else:
        pass
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
