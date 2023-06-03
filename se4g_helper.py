import os
import requests
import pandas as pd
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
from sqlalchemy import create_engine
import codecs


#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
#--                                                                                                                 --#
#--                       <<<<<<                  DATA MANAGEMENT                       >>>>>>                      --#
#--                                                                                                                 --#
#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#




#
countries= ['AD','AT','BA','BE','BG','CH','CY','CZ','DE','ES','DK','EE','FI','SE']
pollutants= ['SO2','NO','NO2','CO','PM10']

########################## DB transition ##########################
'''import psycopg2
ip = '192.168.30.19'
ip = 'localhost'
conn = psycopg2.connect(
    host = ip,
    database = "se4g",
    user = "postgres",
    password = "carIs3198"
)
print('connected with ',ip)'''


def insert_data(table_name, rows, conn, columns):
    cur = conn.cursor()

    # Generate the SQL INSERT statement with specified columns
    insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"

    rows = [
        tuple(
            val.strftime('%Y-%m-%d %H:%M:%S%z') if isinstance(val, datetime) else val
            if val != '' else None  # Replace empty string with None for double precision columns
            for val in row
        )
        for row in rows
    ]

    # Execute the INSERT statement for each row
    cur.executemany(insert_statement, rows)

    # Commit the changes and close the cursor
    conn.commit()
    cur.close()


def table_exists(table_name, conn):
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE LOWER(table_name) = LOWER('{table_name}'))")
    exists = cur.fetchone()[0]
    cur.close()
    return exists


# Update DATABASE
def update_DB(new_rows, connection, table_name='se4g_pollution_DB', columns=None):
    cur = connection.cursor()

    # Generate the SQL SELECT statement
    select_statement = f"SELECT * FROM {table_name}"

    # Execute the SELECT statement
    cur.execute(select_statement)

    # Fetch all the results
    results = cur.fetchall()

    # Get the column names from the cursor description
    all_columns = [desc[0] for desc in cur.description]

    # Use all columns if specific columns are not provided
    if not columns:
        columns = all_columns

    # Convert the results to a set of tuples for efficient comparison
    existing_data = {tuple(row) for row in results}

    # Filter new_rows to only include rows not already present in the table
    filtered_rows = [row for row in new_rows if tuple(row) not in existing_data]

    if len(filtered_rows) == 0:
        print("Nothing to update inside database", table_name)
    else:

        # Execute the INSERT statement to add the filtered rows
        insert_data(table_name, filtered_rows, connection, columns)
        print("Database", table_name, "updated successfully")

    # Close the cursor
    cur.close()

    return filtered_rows


# Download and get the dataframe file name
def download_DB(
    connection,
    COUNTRIES=countries,
    POLLUTANTS=pollutants,
    df_columns=[
        'station_code',
        'station_name',
        'station_altitude',
        'network_countrycode',
        'pollutant',
        'value_datetime_begin',
        'value_datetime_end',
        'value_datetime_updated',
        'value_numeric',
    ],
    table_name='se4g_pollution_DB'
):
    print('-----------------------------------------------------------------------')
    # Set download url
    # https://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm
    ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"

    # Create a cursor
    cur = connection.cursor()

    # Check if the table exists, create it if it doesn't
    if not table_exists(table_name, connection):

        data_type = ['VARCHAR',
            'VARCHAR',
            'FLOAT',
            'CHAR(2)',
            'VARCHAR',
            'VARCHAR',
            'VARCHAR',
            'VARCHAR',
            'FLOAT']
        
        column_definitions = [f"{column} {data_type[i]}" for i, column in enumerate(df_columns)]
        create_table_statement = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
        cur.execute(create_table_statement)
        connection.commit()

    for country in COUNTRIES:
        for pollutant in POLLUTANTS:
            downloadFile = f"{ServiceUrl}/{country}_{pollutant}.csv"
            # Download and save to local path
            print('Downloading:', downloadFile)

            file_content = requests.get(downloadFile).content
            file_content_str = file_content.decode('utf-8-sig')

            # Split the string into lines and split each line by comma (change delimiter as per your CSV format)
            lines = file_content_str.splitlines()
            lines = file_content_str.strip().split('\n')

            print('lines[0]',lines[0])

            if not lines[0].startswith('<!DOCTYPE html'):

                # Create a list of values to be inserted
                data = [line.split(',') for line in lines]

                # Get the column names from the CSV file
                csv_columns = data[0]

                # Create a dictionary to map CSV columns to indices
                csv_column_dict = {col: index for index, col in enumerate(csv_columns)}

                # Filter the data to include only the desired columns
                filtered_data = [[row[csv_column_dict[col]] for col in df_columns] for row in data[1:]]
                
                new_rows = [tuple(row) for row in filtered_data]

                print('Download finished and new_rows assembled')
                print('new_rows[:2] unfiltered',new_rows[:2])

                # Update the database table with new rows if not already present
                updated_rows = update_DB(new_rows, connection, table_name, df_columns)

                return updated_rows

    # Close the cursor and connection
    cur.close()
#conn.close()





########################## CSV ##########################

# Download and get the dataframe file name
def download_request(COUNTRIES= countries,
		     		 POLLUTANTS= pollutants,
					 folder_out = 'data'):
    print('-----------------------------------------------------------------------')
    # Set download url
    # https://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm
    ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"

    dir = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")

    if not os.path.exists(os.path.join(folder_out, dir)):
        if not os.path.exists(folder_out):
            os.mkdir(folder_out)
        os.mkdir(os.path.join(folder_out, dir))
        print(dir, 'directory created')

    for country in COUNTRIES:
        for pollutant in POLLUTANTS:
            fileName = "%s_%s.csv" % (country, pollutant)
            downloadFile = '%s/%s_%s.csv' % (ServiceUrl, country, pollutant)
            # Download and save to local path
            print('Downloading: %s' % downloadFile)

            file_content = requests.get(downloadFile).content
            file_content_str = file_content.decode('utf-8-sig')

            full_file = os.path.join(folder_out, dir, fileName)

            with open(full_file, 'w', encoding='utf-8') as output:
                output.write(file_content_str)

            print('Saved locally as: %s ' % full_file)
            print('-----')
    print('Download finished')
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
				first_line = file.readline().strip()#.decode('utf-8-sig')
                
			
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
            return filtered_rows
    else:
        new_df.to_csv(full_path, index=False)
        print("Dataset ",fileName," created successfully")

def update_dashboard_dataset(df,folder_out = 'data'):
    
    fileName = "se4g_dashboard_dataset.csv"
    full_path = os.path.join(folder_out, fileName)
    
    country = {'AD': 'Andorra', 
           'SE':'Sweden', 
           'DE':'Germany', 
           'CY':'Undefined', 
           'BE':'Belgium', 
           'FI':'Finland', 
           'ES':'Spain', 
           'CZ':'Czech Republic', 
           'BG':'Bulgaria', 
           'BA':'Bosnia and Herzegovina', 
           'EE':'Estonia', 
           'CH':'Switzerland',
           'AT':'Austria', 
           'DK':'Denmark'}


    # Convert 'value_datetime_end' to datetime objects and extract the day
    datetime_objects = df['value_datetime_end'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z'))
    df['day'] = datetime_objects.dt.day
    
    # Compute daily mean of 'value_numeric' for each 'pollutant' and 'network_countrycode'
    daily_mean = df.groupby(['pollutant', 'network_countrycode', 'day'])['value_numeric'].mean().reset_index()
    
    # Merge the daily mean back to the original dataframe
    df = df.merge(daily_mean, on=['pollutant', 'network_countrycode', 'day'], suffixes=('', '_mean'))
    
    # Convert 'value_datetime_end' to int64 type
    #df['value_datetime_end'] = datetime_objects.apply(lambda x: x.strftime('%m%d%H')).astype('int64')

    df['country'] = df['network_countrycode'].map(country)
    #df = df[['pollutant', 'country', 'day', 'value_numeric_mean']].copy()
    df = df[['pollutant', 'country', 'day', 'value_numeric_mean','value_datetime_begin']].copy()

    df = df.drop_duplicates().reset_index(drop=True)
    df = df.sort_values('day')
    
    if os.path.isfile(full_path):
        old_df = pd.read_csv(full_path)
        
        filtered_rows = df[df['value_datetime_begin'] > old_df['value_datetime_begin'].max()]
        if filtered_rows.empty:
            print("Nothing to update inside ",fileName)
        elif not filtered_rows.empty:
            updated_df = pd.concat([old_df, filtered_rows], ignore_index=True)
            updated_df.to_csv(full_path, index=False)
            print("Dataset ",fileName," updated successfully")
    else: 
         df.to_csv(full_path, index=False)
         print("Dataset ",fileName," created successfully")
        

     
     

	

#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
#--                                                                                                                 --#
#--                     <<<<<<               USER LOGIN & REGISTRATION                    >>>>>>                    --#
#--                                                                                                                 --#
#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

class Login:
    def __init__(self):

        folder = 'data'
        filename = 'admins.csv'
        self.path_file = os.path.join(folder,filename)
        if os.path.isfile(self.path_file):
            df = pd.read_csv(self.path_file)
            self.user_list = dict(zip(df['Username'], df['Password']))
    
    def check_credentials(self, username, password):
        if username in self.user_list:
            if self.user_list[username] == password:
                return True
        return False
    
    def register_user(self, username, password):
        if username not in self.user_list:
            self.user_list[username] = password
            self.save_users_to_csv()
            return True
        return False
    
    def save_users_to_csv(self):
        data = {'Username': list(self.user_list.keys()), 'Password': list(self.user_list.values())}
        df = pd.DataFrame(data)
        df.to_csv(self.filename, index=False)
        print(f"User data saved to {self.filename} successfully.")
        
    
def DB_login():
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

    login = Login()

    def handle_login_button_click(button):
        username = user.value
        password = psw.value

        if login.check_credentials(username, password):
            
            ip = '192.168.30.19'
            db = 'se4g'
            db_username = 'postgres'
            port = '5432'
            # Connect to the database
            file = 'bin.txt'
            with open('code/'+file, 'r') as f:
                engine = create_engine('postgresql://'+db_username+':'+f.read()+'@'+ip+':'+port+'/'+db) 
            con = engine.connect()
            # Perform any necessary database operations
            # ...
            # Return the database connection or perform any other actions
            print("Login successful! Connected with",ip)
            return con
        else:
            print("Invalid username or password.")

    login_button.on_click(handle_login_button_click)
    

class Register:
    def __init__(self):
        folder = 'data'
        filename = 'registrations.csv'
        self.path_file = os.path.join(folder, filename)
        if os.path.isfile(self.path_file):
            df = pd.read_csv(self.path_file)
            self.register_list = dict(zip(df['Username'], df['Password']))
        else:
            self.register_list = {}

        self.login = Login()
    
    def add_registration(self, username, password):
        self.register_list[username] = password
        self.save_registrations_to_csv()
    
    def remove_registration(self, username, password):
        #self.register_list = [(u, p) for u, p in self.register_list if (u, p) != (username, password)]
        if username in self.register_list and self.register_list[username] == password:
            del self.register_list[username]
            self.save_registrations_to_csv()
    
    def review_registrations(self):
        def approve_user(username, password):
            self.login.register_user(username, password)
            self.remove_registration(username, password)
            print(f"{username} admitted!")

        def reject_user(username, password):
            self.remove_registration(username, password)
            print(f"{username} rejected!")

        for username, password in self.register_list.items():
            approve_button = widgets.Button(description='Admit')
            reject_button = widgets.Button(description='Reject')

            approve_button.on_click(lambda _, u=username, p=password: approve_user(u, p))
            reject_button.on_click(lambda _, u=username, p=password: reject_user(u, p))

            display(widgets.HBox([widgets.Label(username), approve_button, reject_button]))
    
    def save_registrations_to_csv(self):
        data = {'Username': list(self.register_list.keys()), 'Password': list(self.register_list.values())}
        df = pd.DataFrame(data)
        df.to_csv(self.path_file, index=False)
        print(f"Registration request saved successfully.")




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

    login = Login()

    def handle_login_button_click(button):
        username = user.value
        password = psw.value

        if login.check_credentials(username, password):
            

            print("Login successful!")
            
        else:
            print("Invalid username or password.")

    login_button.on_click(handle_login_button_click)



#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
#--                                                                                                                 --#
#--                    <<<<<<              DASHBOARD CREATION & VISUALIZATION              >>>>>>                   --#
#--                                                                                                                 --#
#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
