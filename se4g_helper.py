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

def download_request(countries,pollutants,folder_out = 'data'):
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
	return fileName


def build_dataframe(COUNTRIES, 
		    		POLLUTANTS, 
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
				df_temp = pd.read_csv("data/"+fileName)
				#data = df_temp[df_columns]
				dfs.append(df_temp[df_columns])
				#df_all = pd.DataFrame(data)
	df_all = pd.concat(dfs, ignore_index=True)
	print ('Database assembled')
	return df_all

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
