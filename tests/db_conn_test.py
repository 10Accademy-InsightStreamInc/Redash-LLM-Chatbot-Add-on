import unittest
from unittest.mock import patch
from db.db_conn import DatabaseLoader

class TestDatabaseLoader(unittest.TestCase):

    @patch('db.db_conn.os.getenv')
    def test_all_credentials_present(self, mock_os_getenv):
        mock_os_getenv.side_effect = lambda x: {
            'DB_USERNAME': 'redash',
            'DB_PASSWORD': 'password',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_DATABASE': 'test_db'
        }[x]
        db_loader = DatabaseLoader()
        self.assertEqual(db_loader.connection_url, "postgresql+psycopg2://redash:password@localhost:5432/test_db")

    @patch('db.db_conn.os.getenv')
    def test_username_missing(self, mock_os_getenv):
        mock_os_getenv.return_value = None
        with self.assertRaises(ValueError):
            DatabaseLoader()

    # Similarly, add tests for other missing credentials

if __name__ == '__main__':
    unittest.main()