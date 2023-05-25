import unittest
import os
import pandas as pd
from datetime import datetime

# Import the functions from the script
from se4g_helper import download_request, build_dataframe, update_dataset, login_required

class TestScript(unittest.TestCase):
    
    def setUp(self):
        self.folder_out = 'test_data'
        if not os.path.exists(self.folder_out):
            os.mkdir(self.folder_out)
    
    def tearDown(self):
        if os.path.exists(self.folder_out):
            os.rmdir(self.folder_out)
    
    def test_download_request(self):
        # Test download_request function
        
        # Ensure the test data directory is empty
        self.assertEqual(len(os.listdir(self.folder_out)), 0)
        
        # Call the download_request function
        dir = download_request(COUNTRIES=['AD'], POLLUTANTS=['SO2'], folder_out=self.folder_out)
        
        # Check if the directory is created and files are downloaded
        self.assertTrue(os.path.exists(os.path.join(self.folder_out, dir)))
        self.assertEqual(len(os.listdir(os.path.join(self.folder_out, dir))), 1)
        
    def test_build_dataframe(self):
        # Test build_dataframe function
        
        # Prepare the test data
        dir = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
        os.mkdir(os.path.join(self.folder_out, dir))
        test_file = os.path.join(self.folder_out, dir, "AD_SO2.csv")
        with open(test_file, 'w') as file:
            file.write("station_code,station_name,station_altitude,network_countrycode,pollutant,value_datetime_begin,value_datetime_end,value_datetime_updated,value_numeric\n")
            file.write("ABC,Station1,100,AD,SO2,2023-01-01T00:00:00,2023-01-01T01:00:00,2023-01-01T01:30:00,10\n")
        
        # Call the build_dataframe function
        df = build_dataframe(dir, COUNTRIES=['AD'], POLLUTANTS=['SO2'], folder_out=self.folder_out)
        
        # Check if the dataframe is built correctly
        expected_df = pd.DataFrame({
            'station_code': ['ABC'],
            'station_name': ['Station1'],
            'station_altitude': [100],
            'network_countrycode': ['AD'],
            'pollutant': ['SO2'],
            'value_datetime_begin': ['2023-01-01T00:00:00'],
            'value_datetime_end': ['2023-01-01T01:00:00'],
            'value_datetime_updated': ['2023-01-01T01:30:00'],
            'value_numeric': [10]
        })
        pd.testing.assert_frame_equal(df, expected_df)
    
    def test_update_dataset(self):
        # Test update_dataset function
        
        # Prepare the test data
        test_file = os.path.join(self.folder_out, "se4g_pollution_dataset.csv")
        df_existing = pd.DataFrame({
            'station_code': ['XYZ'],
            'station_name': ['Station2'],
            'station_altitude': [200],
            'network_countrycode': ['AD'],
            'pollutant': ['SO2'],
            'value_datetime_begin': ['2023-01-01T02:00:00'],
            'value_datetime_end': ['2023-01-01T03:00:00'],
            'value_datetime_updated': ['2023-01-01T03:30:00'],
            'value_numeric': [20]
        })
        df_new = pd.DataFrame({
            'station_code': ['ABC'],
            'station_name': ['Station1'],
            'station_altitude': [100],
            'network_countrycode': ['AD'],
            'pollutant': ['SO2'],
            'value_datetime_begin': ['2023-01-01T00:00:00'],
            'value_datetime_end': ['2023-01-01T01:00:00'],
            'value_datetime_updated': ['2023-01-01T01:30:00'],
            'value_numeric': [10]
        })
        df_expected = pd.concat([df_existing, df_new], ignore_index=True)
        df_existing.to_csv(test_file, index=False)
        
        # Call the update_dataset function
        update_dataset(df_new, folder_out=self.folder_out)
        
        # Check if the dataset is updated correctly
        df_updated = pd.read_csv(test_file)
        pd.testing.assert_frame_equal(df_updated, df_expected)
    
    def test_login_required(self):
        # Test login_required function
        
        # Create the mock input values
        mock_user = 'postgres'
        mock_password = 'carIs3198'
        
        # Patch the input functions to return the mock input values
        with unittest.mock.patch('builtins.input', side_effect=[mock_user, mock_password]):
            # Call the login_required function
            con = login_required()
        
        # Check if the database connection is returned correctly
        self.assertIsNotNone(con)
    
        # Create the mock input values for invalid credentials
        mock_user = 'invalid'
        mock_password = 'invalid'
        
        # Patch the input functions to return the mock input values
        with unittest.mock.patch('builtins.input', side_effect=[mock_user, mock_password]):
            # Call the login_required function
            con = login_required()
        
        # Check if the database connection is not returned
        self.assertIsNone(con)

# Run the tests
if __name__ == '__main__':
    unittest.main()
