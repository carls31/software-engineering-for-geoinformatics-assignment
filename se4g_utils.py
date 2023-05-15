#Python sample for download of air quality up-to-date files
#The Pyton script shows a simple sample how the pre-processed CSV files can be downloaded.
#EEA takes no responsibility of the script and the code is provided 'as is', without warranty of any kind.
#Peter Kjeld, 15. February 2019
import os
import requests
import pandas as pd
# Set an output folder
folder_out = 'data'

def download_request(countries,pollutants):
	print ('-----------------------------------------------------------------------')
	# Set download url
	ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"

	for country in countries:
		for pollutant in pollutants:
			fileName = "%s_%s.csv" % (country, pollutant)
			downloadFile = '%s/%s_%s.csv' % (ServiceUrl, country, pollutant)
			#Download and save to local path
			print('Downloading: %s' % downloadFile )
			file = requests.get(downloadFile).content
			full_file = os.path.join(folder_out, fileName)
			output = open(full_file, 'wb')
			output.write(file)
			output.close()
			print ('Saved locally as: %s ' % fileName)
			print ('-----')
		print ('Download finished')
	return fileName

df = pd.DataFrame()
df_columns = ['station_code', 'station_name', 'station_altitude', 'network_countrycode', 'pollutant', 'value_datetime_begin','value_datetime_end','value_datetime_updated','value_numeric']
def build_dataframe(countries, pollutants):	
	for country in countries:
		for pollutant in pollutants:
			fileName = "%s_%s.csv" % (country, pollutant)

			#Download and save to local path
			df_temp = pd.read_csv("data/"+fileName)

			# Create a DataFrame from a list of list
			data = [[]]
			df = pd.DataFrame(data,columns=df_columns)

		print ('Database assembled')
