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
# Set an output folder

def download_request(countries= ['AD','AT','BA','BE','BG','CH','CY','CZ','DE','DK','EE','ES','FI','SE'],
		     		 pollutants= ['SO2','CO','O3','PM25','PM10'],
					 folder_out = 'data'):
	print ('-----------------------------------------------------------------------')
	# Set download url
	ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"

	dir = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
	if not os.path.exists(os.path.join(folder_out, dir)):
		os.mkdir(os.path.join(folder_out, dir))
		print(dir,'directory created')
		
	for country in countries:
		for pollutant in pollutants:
			fileName = "%s_%s.csv" % (country, pollutant)
			downloadFile = '%s/%s_%s.csv' % (ServiceUrl, country, pollutant)
			#Download and save to local path
			print('Downloading: %s' % downloadFile )

			file = requests.get(downloadFile).content
			full_file = os.path.join(folder_out, dir, fileName)

			output = open(full_file, 'wb')
			output.write(file)
			output.close()
			print ('Saved locally as: %s ' % fileName)
			print ('-----')
	print ('Download finished')
	return dir


def build_dataframe(dir,
					COUNTRIES = ['AD','AT','BA','BE','BG','CH','CY','CZ','DE','DK','EE','ES','FI','SE'], 
		    		POLLUTANTS = ['SO2','CO','O3','PM25','PM10'], 
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
			if fileName != "FI_CO.csv" and fileName != "CY_PM10.csv":
				df_temp = pd.read_csv("data/"+dir+"/"+fileName)

				dfs.append(df_temp[df_columns])
				
	df_all = pd.concat(dfs, ignore_index=True)
	print ('Database assembled')
	return df_all

def update_dataset(new_df, folder_out = 'data'):

	fileName = "se4g_pollution_dataset.csv"
	full_path = os.path.join(folder_out, fileName)

	# Open the CSV dataset
	df = pd.read_csv(full_path)

	# Update the dataset by adding some data
	updated_df = pd.concat([df, new_df], ignore_index=True)

	# Save the updated dataset
	updated_df.to_csv(full_path, index=False)

	print("Dataset updated and saved successfully.")


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
