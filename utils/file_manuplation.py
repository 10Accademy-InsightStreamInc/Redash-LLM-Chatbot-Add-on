import os
import zipfile
import pandas as pd

class ZipExtractor:
    def __init__(self, folder_path, output_directory):
        self.folder_path = folder_path
        self.output_directory = output_directory
        print(f"Extracting files from {self.folder_path} to {self.output_directory}. and current working directory is {os.getcwd()}")

    def extract_files(self):
        """
        Extracts all .zip files from the input folder and places the extracted .csv files into 
        a subdirectory with the same name as the .zip file.
        The subdirectory will be created in the output directory if it doesn't already exist.
        """

        # Make sure the output directory exists
        os.makedirs(self.output_directory, exist_ok=True)

        # Loop through each file in the input folder
        for zip_file_name in os.listdir(self.folder_path):

            # C--heck if the file is a .zip file
            if zip_file_name.endswith(".zip"):

                # Create the path to the .zip file
                zip_file_path = os.path.join(self.folder_path, zip_file_name)

                # Create a subdirectory with the same name as the .zip file
                output_subdirectory = os.path.join(self.output_directory, zip_file_name[:-4])
                print(f"Creating subdirectory {output_subdirectory} for {zip_file_path}.")
                os.makedirs(output_subdirectory, exist_ok=True)

                # Open the .zip file
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:

                    # Print a message for each extracted file
                    for file_name in zip_ref.namelist():
                        if file_name.endswith(".csv"):
                            print(f"Extracting {file_name} from {zip_file_path} to {output_subdirectory}.")

                    # Extract all .csv files from the .zip file to the subdirectory
                    zip_ref.extractall(output_subdirectory)

        print("Extraction completed.")
    # Function to convert HH:MM:SS to total seconds
    def convert_to_seconds(self, time_str):
        print("The time string is :: ", time_str)
        if isinstance(time_str, str):
            try:
                h, m, s = map(int, time_str.split(':'))
                return h * 3600 + m * 60 + s
            except ValueError:
                return 0  # Handle the case where split fails or conversion fails
        else:
            return 0

    # a function that gets the folder name and moves to the sub directory and looks for csv files named "Table data" and "Chart data" and using pandas merges them on their folder name also uses the folder name for the db write using ".to_sql" found in pandas
    def merge_csv_files(self, conn_engine) -> dict: 
        #Initialize a dict to store the dataframes
        dict_merged_data = {}
        # Iterate through each subdirectory in the output directory
        for subdirectory_name in os.listdir(self.output_directory):

            subdirectory_path = os.path.join(self.output_directory, subdirectory_name)

            # Check if the subdirectory contains the necessary .csv files
            if "Table data.csv" in os.listdir(subdirectory_path) and "Chart data.csv" in os.listdir(subdirectory_path):
                # Load the .csv files into pandas DataFrames
                table_data = pd.read_csv(os.path.join(subdirectory_path, "Table data.csv"))
                chart_data = pd.read_csv(os.path.join(subdirectory_path, "Chart data.csv"))
                
                if "Average view duration" in table_data.columns:
                    table_data['Average view duration'] = table_data['Average view duration'].apply(self.convert_to_seconds)
                    table_data.rename(columns={'Average view duration': 'Average View Duration in seconds'}, inplace=True)
                # if chart data has column DATE convert it to datetime
                #if the 
                # Merge the DataFrames on the folder name
                # city_chart_table_merge = pd.merge(city_chart, city_table, on="City name", how="left")
                merged_data = pd.merge(chart_data, table_data, on=subdirectory_name,  how="left", ) # suffixes=("_chart", "_table")
                # if merged data has column Views_x rename to "Views by Date" and 
                # if it has column Views_y rename to Total Views by the subdirectory name"
                print(merged_data.dtypes)
                if "DATE" in merged_data.columns:
                    merged_data["DATE"] = pd.to_datetime(merged_data["DATE"])
                if "City name_y" and "City name_x" in merged_data.columns:
                    merged_data.drop('City name_y', axis=1, inplace=True)
                    merged_data.rename(columns={'City name_x': 'City name'}, inplace=True)
                if "Views_x" in merged_data.columns:
                    merged_data = merged_data.rename(columns={"Views_x": "Views by Date"})
                if "Views_y" in merged_data.columns:
                    merged_data.drop('Views_y', axis=1, inplace=True)
                    # merged_data = merged_data.rename(columns={"Views_y": f"Total Views by {subdirectory_name}"})
                if "Shares_x" in merged_data.columns:
                    merged_data = merged_data.rename(columns={"Shares_x": "Shares by Date"})
                if "Shares_y" in merged_data.columns:
                    merged_data.drop('Shares_y', axis=1, inplace=True)
                    # merged_data = merged_data.rename(columns={"Shares_y": f"Total Shares by {subdirectory_name}"})
                if "Subscribers_x" in merged_data.columns:
                    merged_data = merged_data.rename(columns={"Subscribers_x": "Subscribers by Date"})
                if "Subscribers_y" in merged_data.columns:
                    merged_data.drop('Subscribers_y', axis=1, inplace=True)

                table_columns = table_data.columns.tolist()
                
                # Rename columns from 'Table data' to include 'Total'
                for column in table_columns:
                    if column in merged_data.columns and \
                    (merged_data.dtypes[column] == "int64" or merged_data.dtypes[column] == "float64"):
                        if column.startswith('Average'):
                            continue
                        new_column_name = 'Total ' + column + ' by ' + subdirectory_name
                        merged_data.rename(columns={column: new_column_name}, inplace=True)

                # store the merged data into a dictionary "merged_data" using subdirectory name
                dict_merged_data[subdirectory_name] = merged_data

                # Write the merged data to a database table
                #merged_data.to_sql(subdirectory_name, conn_engine, if_exists="replace", index=False)
        print("Data merge and write completed.")
        return dict_merged_data
    
    # a function that accepts dictionary of merged dataframes and writes them to the database
    def write_to_db(self, dict_merged_data, conn_engine):
        """
        This function takes in a dictionary of merged dataframes and writes them to a database using the pandas
        to_sql method. The key of each item in the dictionary is the table name, and the value is the merged dataframe.
        The function iterates through each key-value pair in the dictionary, and calls the to_sql method to write the
        dataframe to a database table. If the table already exists, it replaces it.
        """
        for table_name, merged_data in dict_merged_data.items():
            print(f"Writing {table_name} to database...")
            # Write the merged data to a database table
            merged_data.to_sql(table_name, conn_engine, if_exists="replace", index=False)
        print("Data write to database completed.")

