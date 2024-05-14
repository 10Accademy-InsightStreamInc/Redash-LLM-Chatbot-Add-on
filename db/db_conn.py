import pandas as pd
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import sessionmaker
import os
# from dotenv import load_dotenv
import sys

class DatabaseLoader:
    def __init__(self):
        """
        Initialize the database connection object with the provided database credentials.
        Fetches database credentials from environment variables and constructs the connection URL.
        Raises a ValueError if any of the required credentials are missing.
        """
        # Load environment variables from the .env file
        # load_dotenv()
        # postgres://abuki:RO2Wa1UIBqV0fHU6Wu1SbYQvN2HJx0Rn@dpg-cp083no21fec73fvqci0-a.oregon-postgres.render.com/redash_llm_db_cmt5
        # Fetch database credentials from environment variables
        self.username = 'abuki' # os.getenv("DB_USERNAME")
        self.password = 'RO2Wa1UIBqV0fHU6Wu1SbYQvN2HJx0Rn' # os.getenv("DB_PASSWORD")
        self.host = 'dpg-cp083no21fec73fvqci0-a.oregon-postgres.render.com' # os.getenv("DB_HOST")
        self.port = 5432 # os.getenv("DB_PORT")
        self.database = 'redash_llm_db_cmt5' # os.getenv("DB_DATABASE")

        # Check if any credentials are missing
        if None in (self.username, self.password, self.host, self.port, self.database, self.host):
            raise ValueError("One or more database credentials are missing.")

        self.connection_url = f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = None
        self.connection = None
    
    def connect(self):
        """
        Establishes a connection to the database.

        This function creates a connection engine using the provided connection URL and establishes a connection to the database.
        If the connection is successful, it prints a message indicating that the connection has been established.
        If an exception occurs during the connection process, it prints an error message with the specific exception details.

        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.

        Returns:
            None
        """
        try:
            self.engine = create_engine(self.connection_url)
            self.connection = self.engine.connect()
            print("Connected to the database.")
            return self.connection
        except Exception as e:
            print(f"Error connecting to the database: {str(e)}")

    def execute_query(self, query):
        """
        Executes a SQL query on the database.

        This function executes the provided SQL query on the database using the connection object.
        If the query is successful, it prints a message indicating that the query has been executed.
        If an exception occurs during the query execution, it prints an error message with the specific exception details.

        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.
            query (str): The SQL query to be executed.

        Returns:
            None
        """
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error executing query: {str(e)}")

    def create_db(self, db_name: str):
        try:
            with self.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT")
                conn.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}") 
                self.connection_url = f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}"
                conn.close()
        except Exception as e:
            print(f"Error while inserting to table: {e}")  
            sys.exit(e)

    def set_connection_url_from_dbname(self, dbname: str):
        self.database = dbname
        self.connection_url = f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{dbname}"

        print("The new conn url is :: ", self.connection_url)

    def close(self):
        """
        Closes the connection to the database.

        This function checks if the connection to the database is open and closes it if it is.
        If the connection is successfully closed, it prints a message indicating that the connection has been disconnected.

        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.

        Returns:
            None
        """
        if self.connection:
            self.connection.close()
            print("Disconnected from the database.")
    def drop_all_tables(self):
        """
        Drops all tables in the database.

        This function drops all tables in the database using the connection object.
        If the operation is successful, it prints a message indicating that all tables have been dropped.
        If an exception occurs during the table dropping process, it prints an error message with the specific exception details.

        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.

        Returns:
            None
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            for table in tables:
                print(f"Dropping table: {table}")
                self.connection.execute(text(f'DROP TABLE IF EXISTS "{table}"'))

        except Exception as e:
            print(f"Error dropping tables: {str(e)}")

    def add_data_to_table(self, df: pd.DataFrame, table_name: str):
        """
        Adds data to a table in the database.

        This function takes a pandas DataFrame and a table name as input and inserts the data into the table.

        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.
            df (pandas.DataFrame): The DataFrame containing the data to be inserted.
            table_name (str): The name of the table to which the data should be inserted.

        Returns:
            None
        """
        df.to_sql(table_name, self.engine, if_exists='append', index=False)
    def get_table_column_names(self):
        """
        This function retrieves the names of all tables in the database and their corresponding columns.
        It returns a dictionary where the keys are the table names and the values are lists of column
        dictionaries. Each column dictionary contains information about the column, such as its name,
        data type, and whether it is nullable.

        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.

        Returns:
            dict: A dictionary where the keys are table names and the values are lists of column dictionaries.
        """
        # Initialize an empty dictionary to store the table names and their corresponding columns.
        table_column_dict = {}

        # Iterate over each table in the database.
        for table in self.inspector.get_table_names():
            # Retrieve the columns of the current table.
            columns = self.inspector.get_columns(table)

            # Add the table name and its corresponding columns to the dictionary.
            table_column_dict[table] = columns

        return table_column_dict


    def clean_inspector_db(self, table_column_dict: dict):
        """
        This function takes a dictionary of table names and their corresponding column names as input.
        It modifies the dictionary by removing all the key-value pairs except for the column name and 
        renaming the key to be the table name and the value to be the column name. 
        
        Parameters:
            self (DatabaseConnection): The instance of the DatabaseConnection class.
            table_column_dict (dict): A dictionary where the keys are table names and the values are lists of column names.
        
        Returns:
            None
        """
        # Iterate over each table in the dictionary
        for table_name, columns in table_column_dict.items():
            # Create a new list that contains only the column names
            column_names = [column['name'] for column in columns]
            # Remove all the key-value pairs from the dictionary
            table_column_dict.clear()
            # Add a new key-value pair to the dictionary with the table name as the key and the column name as the value
            table_column_dict[table_name] = column_names

        return table_column_dict
  
    def __del__(self):
        self.close()