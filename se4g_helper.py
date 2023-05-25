#Python sample for download of air quality up-to-date files
#The Pyton script shows a simple sample how the pre-processed CSV files can be downloaded.
#EEA takes no responsibility of the script and the code is provided 'as is', without warranty of any kind.
#Peter Kjeld, 15. February 2019
import os
import requests
import pandas as pd
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
from sqlalchemy import create_engine
# 
countries= ['AD','AT','BA','BE','BG','CH','CY','CZ','DE','ES','DK','EE','FI','SE']
pollutants= ['SO2','NO','NO2','CO','PM10']

# Download and get the dataframe file name
def download_request(COUNTRIES= countries,
		     		 POLLUTANTS= pollutants,
					 folder_out = 'data'):
	print ('-----------------------------------------------------------------------')
	# Set download url
	# https://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm
	ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"
	

	dir = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")

	if not os.path.exists(os.path.join(folder_out, dir)):
		if not os.path.exists(folder_out):
			os.mkdir(folder_out)
		os.mkdir(os.path.join(folder_out, dir))
		print(dir,'directory created')
		
	for country in COUNTRIES:
		for pollutant in POLLUTANTS:
			fileName = "%s_%s.csv" % (country, pollutant)
			downloadFile = '%s/%s_%s.csv' % (ServiceUrl, country, pollutant)
			#Download and save to local path
			print('Downloading: %s' % downloadFile )

			file = requests.get(downloadFile).content
			full_file = os.path.join(folder_out, dir, fileName)

			output = open(full_file, 'wb')
			output.write(file)
			output.close()
			print ('Saved locally as: %s ' % full_file)
			print ('-----')
	print ('Download finished')
	return dir

# Build the dataframe with the required structure
def build_dataframe(dir,
					COUNTRIES = countries, 
		    		POLLUTANTS = pollutants, 
				    folder_out = 'data',
		    		df_columns = ['station_code', 
							      'station_name', 
								  'station_altitude', 
								  'network_countrycode', 
								  'pollutant', 
								  'value_datetime_begin',
								  'value_datetime_end',
								  'value_datetime_updated',
								  'value_numeric'] ):	
	dfs = []
	for country in COUNTRIES:
		for pollutant in POLLUTANTS:

			fileName = "%s_%s.csv" % (country, pollutant)
			print(fileName)
			file_path = os.path.join(folder_out, dir, fileName)
			'''
			_, file_extension = os.path.splitext(file_path)
			if file_extension == ".csv" and os.path.isfile(file_path):
			'''
			with open(file_path, 'r') as file:
				print(file)
				first_line = file.readline().strip()
			
			if not first_line.startswith('<!DOCTYPE html'): #first_line.startswith('network_countrycode'):
				#print(fileName,'exist')

				df_temp = pd.read_csv(file_path)
				dfs.append(df_temp[df_columns])
				
	df_all = pd.concat(dfs, ignore_index=True)
	print ('Database assembled')
	return df_all

# Update the final dataset
def update_dataset(new_df, folder_out = 'data'):

	fileName = "se4g_pollution_dataset.csv"
	full_path = os.path.join(folder_out, fileName)

	if os.path.isfile(full_path):
		# Open the CSV dataset
		df = pd.read_csv(full_path)
		df['value_datetime_begin'] = pd.to_datetime(df['value_datetime_begin'])
		new_df['value_datetime_begin'] = pd.to_datetime(new_df['value_datetime_begin'])

		# Filter rows from new_df based on the datetime
		filtered_rows = new_df[new_df['value_datetime_begin'] > df['value_datetime_begin'].max()]
		if filtered_rows.empty:
			print("Nothing to update inside dataset ",fileName)
		elif not filtered_rows.empty:
			# Update the dataset by adding the filtered rows
			updated_df = pd.concat([df, filtered_rows], ignore_index=True)

			# Save the updated dataset
			updated_df.to_csv(full_path, index=False)
			print("Dataset ",fileName," updated successfully")

			# Save locally for backup
			'''backup_dir = "C:/Users/Utente/Documents/GitHub/SE4GEO-backup"
			updated_df.to_csv(backup_dir, index=False)'''

	else:
		new_df.to_csv(full_path, index=False)
		print("Dataset ",fileName," created successfully")

	


# User login 
def login_required():
    user = widgets.Text(
        placeholder='Type postgres',
        description='Username:',
        disabled=False   
    )

    psw = widgets.Password(
        placeholder='Enter password',
        description='Password:',
        disabled=False
    )
    
    login_button = widgets.Button(description="Login")
    display(user, psw, login_button)

    def handle_login_button_click(button):
        username = user.value
        password = psw.value

        # Check if username and password are valid
        if username == "postgres" and password == "carIs3198":
            # Connect to the database
            engine = create_engine('postgresql://'+username+':'+password+'@localhost:5432/se4g') 
            con = engine.connect()
            # Perform any necessary database operations
            # ...
            # Return the database connection or perform any other actions
            print('connected with localhost')
            return con
        else:
            print('it does not work')

    login_button.on_click(handle_login_button_click)
