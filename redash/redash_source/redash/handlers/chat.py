from flask import request, jsonify
from redash.handlers.base import (
    BaseResource
)
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

VARIABLE_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(
  api_key=VARIABLE_KEY
)
# postgres://redash:cKY0oBb7ye17X1ysvMIbehfkyBTvSjls@dpg-cotrfcv109ks73d3v500-a.oregon-postgres.render.com/
username = "redash"
password = "cKY0oBb7ye17X1ysvMIbehfkyBTvSjls"
host = "dpg-cotrfcv109ks73d3v500-a.oregon-postgres.render.com"
port = 5432
database = "redash_llm_db"

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
        new_table_column_dict[key.replace(" ", "_") + "_Table_Name"] = key
        new_table_column_dict[key + "_Columns"] = value

    new_table_column_string = ", ".join([f'{key} {value}' for key, value in new_table_column_dict.items()])

    def get_data_source(self):
        if self.current_user.has_permission("admin"):
            data_sources = models.DataSource.all(self.current_org)
        else:
            data_sources = models.DataSource.all(self.current_org, group_ids=self.current_user.group_ids)

        response = {}
        for ds in data_sources:
            if ds.id in response:
                continue

            try:
                d = ds.to_dict()
                d["view_only"] = all(project(ds.groups, self.current_user.group_ids).values())
                response[ds.id] = d
            except AttributeError:
                print("Error with DataSource#to_dict (data source id: %d)", ds.id)

        self.record_event(
            {
                "action": "list",
                "object_id": "admin/data_sources",
                "object_type": "datasource",
            }
        )
        sort = sorted(list(response.values()), key=lambda d: d["name"].lower())
        return sort
    def post(self):
        try:
            value = request.get_json()
            question = value.get('question')
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages = [
                    {"role": "system",
                        "content": f"You are a helpful assistant who generates SQL queries on the database and responds from the database schema provided only\
                        SQL should be written using this table and column data from database schema: {self.new_table_column_string}\
                        All the tables and columns MUST ALWAYS be in double quotes \
                        The Database you will be writting SQL queries for is: postgres \
                        You are always to the point and ALWAYS generate the SQL query and no additional explanation or text\
                        Generate only SQL syntax when prompted about any inquiries regarding SQL queries.\
                        The query should be returned in plain text, not in JSON \
                        Output should be a fully formed SQL query.\
                        Do not use any kind of formatting on your response query such as newlines or indentation finish everything in one line. \
                        Don't complicate things. Generate only SQL syntax when prompted about any inquiries regarding SQL queries."},
                    {"role": "user", "content": f"{question}"}
                    # "Give me all cities names with there total views and watch time"
                ]
            )
            answer = completion.choices[0].message.content
            response_data = {"answer": f"{answer}"}
            return jsonify(response_data), 200
        except Exception as error:
            print(error)
            return jsonify({"error": "An error occurred"}), 500
        
    # def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": "Bearer " + openai.api_key,
    #     }
    #     json_data = {"model": model, "messages": messages}
    #     if tools is not None:
    #         json_data.update({"tools": tools})
    #     if tool_choice is not None:
    #         json_data.update({"tool_choice": tool_choice})
    #     try:
    #         response = requests.post(
    #             "https://api.openai.com/v1/chat/completions",
    #             headers=headers,
    #             json=json_data,
    #         )
    #         return response.json()
    #     except Exception as e:
    #         print("Unable to generate ChatCompletion response")
    #         print(f"Exception: {e}")
    #         return e