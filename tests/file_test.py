import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from utils.file_manuplation import ZipExtractor

class TestZipExtractor(unittest.TestCase):
    def setUp(self):
        self.folder_path = tempfile.mkdtemp()
        self.output_directory = tempfile.mkdtemp()
        self.extractor = ZipExtractor(self.folder_path, self.output_directory)

    def tearDown(self):
        os.rmdir(self.folder_path)
        os.rmdir(self.output_directory)

    def test_extract_files(self):
        # Create a test .zip file
        zip_file_name = 'test.zip'
        zip_file_path = os.path.join(self.folder_path, zip_file_name)
        with zipfile.ZipFile(zip_file_path, 'w') as zip_ref:
            zip_ref.writestr('test.csv', 'test,data')

        # Call the function being tested
        self.extractor.extract_files()

        # Check that the output directory was created
        output_subdirectory = os.path.join(self.output_directory, 'test')
        self.assertTrue(os.path.isdir(output_subdirectory))

        # Check that the .csv file was extracted to the output directory
        csv_file_path = os.path.join(output_subdirectory, 'test.csv')