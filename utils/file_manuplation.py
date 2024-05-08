import os
import zipfile

class ZipExtractor:
    def __init__(self, folder_path, output_directory):
        self.folder_path = folder_path
        self.output_directory = output_directory
        print(f"Extracting files from {self.folder_path} to {self.output_directory}. and current working directory is {os.getcwd()}")

    def extract_files(self):
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)

        # Iterate through each .zip file in the folder
        for zip_file_name in os.listdir(self.folder_path):
            if zip_file_name.endswith(".zip"):
                zip_file_path = os.path.join(self.folder_path, zip_file_name)

                # Create a subdirectory for each .zip file
                output_subdirectory = os.path.join(self.output_directory, zip_file_name[:-4])
                print(f"Extracting {zip_file_path} to {output_subdirectory}.")
                os.makedirs(output_subdirectory, exist_ok=True)

                # Extract .csv files from the current .zip file to the subdirectory
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_subdirectory)

        print("Extraction completed.")