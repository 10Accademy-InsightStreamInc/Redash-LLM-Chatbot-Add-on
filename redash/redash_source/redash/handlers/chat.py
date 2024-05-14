from flask import request, jsonify, Flask
import json
from sqlalchemy import text
from redash.handlers.base import (
    BaseResource
)
from tenacity import retry, wait_random_exponential, stop_after_attempt
import os
from openai import OpenAI
from funcy import project
from redash import models
from redash.handlers.base import (
    BaseResource,
    get_object_or_404,
    require_fields,
)
import requests
from sqlalchemy import create_engine, inspect
app = Flask(__name__)
VARIABLE_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
  api_key=VARIABLE_KEY
)
# postgres://redash:cKY0oBb7ye17X1ysvMIbehfkyBTvSjls@dpg-cotrfcv109ks73d3v500-a.oregon-postgres.render.com/
username = "abuki"
password = "RO2Wa1UIBqV0fHU6Wu1SbYQvN2HJx0Rn"
host = "dpg-cp083no21fec73fvqci0-a.oregon-postgres.render.com"
port = 5432
database = "redash_llm_db_cmt5"

db_conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}"
class ChatResource(BaseResource):
    engine = create_engine(db_conn_str)

    inspector = inspect(engine)

    table_column_dict = {}

    for table in inspector.get_table_names():
        table_column_dict[table] = inspector.get_columns(table)

    for data in table_column_dict:
    #remove all except name and add the nameing Like Table Name for tabl_name and Column for columns
        table_column_dict[data] = [i['name'] for i in table_column_dict[data]]
    
    new_table_column_dict = {}
    for key, value in table_column_dict.items():
        new_table_column_dict[key + " Table Name"] = key
        new_table_column_dict[key + " Columns"] = value
    
    new_table_column_string = ""
    for key, value in new_table_column_dict.items():
        # run the below code every two times
        if type(value) == list:
            new_table_column_string = new_table_column_string + f' and has Columns: ' + ', '.join(value) + ' and \n'
        else:
            new_table_column_string = new_table_column_string + key + ' is: ' + value

    def ask_database(self, query):
        """Function to query Postgres database with a provided SQL query."""
        try:
            # Assuming 'db.connection' is your SQLAlchemy connection
            result = self.engine.connect().execute(text(query)).fetchall()
            return result
        except Exception as e:
            results = f"query failed with error: {e}"
        return results

    def execute_function_call(self, message):
        if message["tool_calls"][0]["function"]["name"] == "ask_database":
            query = json.loads(message["tool_calls"][0]["function"]["arguments"])["query"]
            print("The query is: ", query)
            results = self.ask_database(f'{query}')
        else:
            results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
        return results
    
    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def post(self):
        try:
            value = request.get_json()
            question = value.get('question')
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = [
                {"role": "system",
                    "content": f'''You are a helpful assistant who generates SQL queries on the database and responds from the database schema provided only\
                    SQL should be written using this table and column names from database schema: {self.new_table_column_string}\
                    Table Names or Column Names Referenced anywhere in your SQL Query when writing SQL MUST ALWAYS be in double quotes EVEN IF THEY ARE A SINGLE WORD, \
                    The Database you will be writting SQL queries for is: postgres \
                    You are always to the point and ALWAYS generate the SQL query and no additional explanation or text\
                    Generate only SQL syntax when prompted about any inquiries regarding SQL queries.\
                    The query should be returned in plain text, not in JSON \
                    Output should be a fully formed SQL query.\
                    Please YOU MUST USE DOUBLE QUOTES like "" in FROM, SELECT, WHERE, GROUP BY, ORDER BY, LIMIT and  all other clauses and on \
                    all function in SQL on column names such as SUM() inside MUST BE CALLED WITH COLUMNS IN DOUBLE QUOTES for example if the Column name to be summed is City then use SUM("City") and others builtin SQL functions ARE MUST TO ADD QUOTES OR DONT ANSWER. \
                    Example Like this: 'SELECT "City name", SUM("Views by Date") AS total_views, SUM("Total Watch time (hours) by Citiy name") AS total_watch_time FROM "Cities" GROUP BY "City name"'
                    Do not use any kind of formatting on your response query such as newlines or indentation finish everything in one line. \
                    Don't complicate things. Generate only SQL syntax when prompted about any inquiries regarding SQL queries.'''},
                {"role": "user", "content": f"{question}"},
            ])
            # tools = [
            #     {"type": "function",
            #         "function": {
            #             "name": "ask_database",
            #             "description": "Use this function to answer user questions about music. Input should be a fully formed SQL query.",
            #             "parameters": {
            #                 "type": "object",
            #                 "properties": {
            #                     "query": {
            #                         "type": "string",
            #                         "description": f"""
            #                                 SQL query extracting info to answer the user's question.
            #                                 SQL should be written using this database schema:
            #                                 {self.new_table_column_string}
            #                                 The query should be returned in plain text, not in JSON.
            #                                 """,
            #                     }
            #                 },
            #                 "required": ["query"],
            #             },
            #         }
            #     }
            # ]
            
            # resp = self.chat_completion_request(messages, tools, tool_choice=None, model=model)
                    # "Give me all cities names with there total views and watch time"
            # )
            message = completion["choices"][0]["message"]
            # query = json.loads(message["tool_calls"][0]["function"]["arguments"])["query"]
            # answer = self.execute_function_call(message)
            answer = message["content"]
            # if answer == None:
            #     answer = "Hello this me abuki not ai"
            # if message == None:
            #     message = "This is the first message"
            response_data = {"answer": f"{answer}"}
            return jsonify(response_data), 200
        except Exception as error:
            print(error)
            return jsonify({"error": "An error occurred"}), 500

    @staticmethod    
    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(messages, tools=None, tool_choice=None, model="gpt-3.5-turbo-0613"):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer ",
        }
        json_data = {"model": model, "messages": messages}
        if tools is not None:
            json_data.update({"tools": tools})
        if tool_choice is not None:
            json_data.update({"tool_choice": tool_choice})
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            return response.json()
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
if __name__ == "__main__":
    app.run(debug=True)