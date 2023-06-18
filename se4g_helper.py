'''Authors:  Lorenzo Carlassara - mail: lorenzo.carlassara@mail.polimi.it
            Angelica Iseni      -       angelica.iseni@mail.polimi.it
            Emma Lodetti        -       emma.lodetti@mail.polimi.it
            Virginia Valeri     -       virginia.valeri@mail.polimi.it
'''

import os
import requests
import pandas as pd
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium import plugins
import matplotlib.pyplot as plt
from jupyter_dash import JupyterDash
import dash
from dash import dcc
from dash import html
from bokeh.plotting import figure, show
from bokeh.palettes import Category10
from bokeh.models import ColumnDataSource
from bokeh.io import output_notebook


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

######################################################################################################################
#                                                  DB transition                                                     #
######################################################################################################################

# Connect to DB
file = 'bin.txt'

db_user = "postgres"

ip = '192.168.30.19'
ip = 'localhost'

database = "se4g"
port = "5432"

import psycopg2

def connect_right_now(
    file: str = file,
    db_user: str = db_user,
    ip: str = ip,
    database: str = database,
):
    try:
        with open('code/'+file, 'r') as f:
            conn = psycopg2.connect(
                host = ip,
                database = database,
                user = db_user,
                password = f.read()
            )
        #print('connected with ',ip, ' through psycopg2')
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")

from sqlalchemy import create_engine
def connect_with_sqlalchemy(
    file: str = file,
    db_user: str = db_user,
    ip: str = ip,
    database: str = database,
    port: str = port
):
    try:
        with open('code/'+file, 'r') as f:
            engine = create_engine(f'postgresql://{db_user}:{f.read()}@{ip}:{port}/{database}') 
        #print('connected with ',ip, ' through sqlalchemy')
        return engine
    except create_engine.Error as e:
        print(f"Error connecting to the database: {e}")

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
def update_DB(new_rows, connection, table_name='se4g_pollution_DB', columns=None, file_name=None):
    cur = connection.cursor()

    # Generate the SQL SELECT statement
    select_statement = f"SELECT * FROM {table_name}"

    # Execute the SELECT statement
    cur.execute(select_statement)

    # Fetch all the results
    results = cur.fetchall()

    # Get the column names from the cursor description
    #all_columns = [desc[0] for desc in cur.description]

    # Use all columns if specific columns are not provided
    #if not columns:
    #    columns = all_columns

    # Convert the results to a set of tuples for efficient comparison
    existing_data = {tuple(row) for row in results}

    # Filter new_rows to only include rows not already present in the table
    filtered_rows = [row for row in new_rows if tuple(row) not in existing_data]

    if len(filtered_rows) == 0:
        print("Nothing to update inside database", table_name)
    else:

        # Execute the INSERT statement to add the filtered rows
        insert_data(table_name, filtered_rows, connection, columns)
        print(f"Added to table {table_name}")

    # Close the cursor
    cur.close()

    return filtered_rows

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
        'samplingpoint_x',
        'samplingpoint_y'
    ]

data_type = ['VARCHAR',
            'VARCHAR',
            'FLOAT',
            'CHAR(2)',
            'VARCHAR',
            'VARCHAR',
            'VARCHAR',
            'VARCHAR',
            'FLOAT',
            'FLOAT',
            'FLOAT']

# Download and get the dataframe file name
def download_DB(
    conn,
    COUNTRIES=countries,
    POLLUTANTS=pollutants,
    df_columns=df_columns,
    table_name='se4g_pollution_main'
    #table_name='se4g_pollution_DB'
):
    print('-----------------------------------------------------------------------')
    # Set download url
    # https://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm
    ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"

    # Create a cursor
    cur = conn.cursor()

    # Check if the table exists, create it if it doesn't
    if not table_exists(table_name, conn):

        data_type = data_type
        
        column_definitions = [f"{column} {data_type[i]}" for i, column in enumerate(df_columns)]
        create_table_statement = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
        cur.execute(create_table_statement)
        conn.commit()
    print('countries', COUNTRIES)
    all_rows = []
    for country in COUNTRIES:
        for pollutant in POLLUTANTS:
            downloadFile = f"{ServiceUrl}/{country}_{pollutant}.csv"
            # Download and save to local path
            print(f'Downloading: {ServiceUrl}/{country}_{pollutant}')

            file_content = requests.get(downloadFile).content
            file_content_str = file_content.decode('utf-8-sig')

            # Split the string into lines and split each line by comma (change delimiter)
            lines = file_content_str.splitlines()
            lines = file_content_str.strip().split('\n')

            print('File first line:',lines[0][0:20])

            if not lines[0].startswith('<!DOCTYPE html'):

                # Create a list of values to be inserted
                data = [line.split(',') for line in lines]

                # Get the column names from the file
                columns = data[0]

                # Create a dictionary to map columns to indices
                column_dict = {col: index for index, col in enumerate(columns)}

                # Filter the data to include only the desired columns
                filtered_data = [[row[column_dict[col]] for col in df_columns] for row in data[1:]]
                
                new_rows = [tuple(row) for row in filtered_data]

                print(f'{country}_{pollutant} downloaded --> new_rows assembled')
                #print('new_rows[:2] unfiltered',new_rows[:2])

                # Update the database table with new rows if not already present
                updated_rows = update_DB(new_rows, conn, table_name, df_columns,f"{country}_{pollutant}")
                all_rows.append(updated_rows)

    print("Table", table_name, "updated successfully")

    # Close the cursor 
    cur.close()
    conn.close()
    return all_rows

######################################################################################################################
#                                                      DB from CSV                                                   #                                              
######################################################################################################################

def insert_data_from_CSV(table_name, df, conn, df_columns = df_columns):
    cur = conn.cursor()

    # Iterate over the DataFrame rows and insert data row by row
    for _, row in df.iterrows():
        # Generate the SQL INSERT statement
        insert_statement = f"INSERT INTO {table_name} ({', '.join(df_columns)}) VALUES ({', '.join(['%s'] * len(df_columns))})"
        values = tuple(row[col] for col in df_columns)

        # Execute the INSERT statement
        cur.execute(insert_statement, values)

    
    # Commit the changes and close the cursor 
    conn.commit()
    cur.close()


def update_DB_from_CSV(new_df, connection, engine, table_name='se4g_pollution'):

    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)

    df['value_datetime_begin'] = pd.to_datetime(df['value_datetime_begin'])
    new_df['value_datetime_begin'] = pd.to_datetime(new_df['value_datetime_begin'])
    #new_df.loc[:, 'value_datetime_begin'] = pd.to_datetime(new_df['value_datetime_begin'])

    # Filter rows from new_df based on the datetime
    #filtered_rows = new_df[new_df['value_datetime_begin'] > df['value_datetime_begin'].max()]
    #filtered_rows = pd.concat([new_df, df], ignore_index=True).drop_duplicates()

    # Merge new_df and df to identify the rows in new_df that are not in df
    merged_df = new_df.merge(df, indicator=True, how='left')

    # Select the rows from new_df that are not present in df
    filtered_rows = merged_df[merged_df['_merge'] == 'left_only'].drop(columns='_merge')
    # filtered_rows contains the rows from new_df that are not present in df

    if filtered_rows.empty:
        print("Nothing to update inside database ",table_name)

    elif not filtered_rows.empty:

        # Update the dataset by adding the filtered rows
        #filtered_rows.to_sql(table_name, engine, if_exists='append', index=False)

        # Update the dataset by adding the filtered rows
        insert_data_from_CSV(table_name, filtered_rows, connection)
        print("Database ",table_name," updated successfully")

        return filtered_rows

def update_dashboard_table(conn,
                           engine,
                           dataset = 'se4g_dashboard_dataset.csv',
                           folder = 'data_prova',
                           table_name = "se4g_dashboard"):
    cur = conn.cursor()

    cur.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.commit()

    cur.close()
    conn.close()

    full_path = os.path.join(os.getcwd(),folder,dataset)
    df = pd.read_csv(full_path)
    df.to_sql(table_name, engine, if_exists = 'append', index=False)
    engine.dispose()
    print("Table", table_name, "updated successfully")

def update_dashboard_DB_from_CSV(new_rows, connection, engine, table_name='se4g_dashboard',
    columns = ['pollutant', 'country', 'month_day', 'value_numeric_mean', 'value_datetime_begin']):
    country = {'AD': 'Andorra', 'SE': 'Sweden', 'DE': 'Germany', 'CY': 'Undefined', 'BE': 'Belgium',
               'FI': 'Finland', 'ES': 'Spain', 'CZ': 'Czech Republic', 'BG': 'Bulgaria', 'BA': 'Bosnia and Herzegovina',
               'EE': 'Estonia', 'CH': 'Switzerland', 'AT': 'Austria', 'DK': 'Denmark'}

    # Convert 'value_datetime_end' to datetime objects
    datetime_objects = new_rows['value_datetime_end'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z'))
    new_rows['month_day'] = datetime_objects.dt.strftime('%m%d')
    new_rows['value_datetime_begin'] = pd.to_datetime(new_rows['value_datetime_begin']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Compute daily mean of 'value_numeric' for each 'pollutant' and 'network_countrycode'
    daily_mean = new_rows.groupby(['pollutant', 'network_countrycode', 'month_day'])['value_numeric'].mean().reset_index()
    # Apply round( , 3) to all elements in daily_mean
    daily_mean = daily_mean.apply(lambda x: round(x, 3))

    # Merge the daily mean back to the original dataframe
    new_rows = new_rows.merge(daily_mean, on=['pollutant', 'network_countrycode', 'month_day'], suffixes=('', '_mean'))

    new_rows['country'] = new_rows['network_countrycode'].map(country)
    new_rows = new_rows.drop_duplicates().reset_index(drop=True)
    new_rows = new_rows.sort_values('month_day')
    new_rows = new_rows[columns].copy()

    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)

    df_value_datetime_begin = pd.to_datetime(df['value_datetime_begin']).dt.strftime('%Y-%m-%d %H:%M:%S')

    print("New rows: \n",new_rows)
    print("Max value_datetime_begin in new_rows: \n",new_rows['value_datetime_begin'].max())
    print("Max value_datetime_begin in df: \n",df['value_datetime_begin'].max())
    
    filtered_rows = new_rows[new_rows['value_datetime_begin'] > df_value_datetime_begin.max()]

    if filtered_rows.empty:
        print("Nothing to update inside database", table_name)
    else:
        insert_data_from_CSV(table_name, filtered_rows, connection, df_columns=columns)
        print("Database", table_name, "updated successfully")

######################################################################################################################
#                                                          CSV                                                       #
######################################################################################################################

# Download and get the dataframe file name
def download_request(COUNTRIES= countries,
		     		 POLLUTANTS= pollutants,
					 folder_out = 'data'):
    print('-----------------------------------------------------------------------')
    # Set download url
    # https://discomap.eea.europa.eu/map/fme/AirQualityUTDExport.htm
    ServiceUrl = "http://discomap.eea.europa.eu/map/fme/latest"

    dir = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

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
                    df_columns = df_columns ):	
    dfs = []
    for country in COUNTRIES:
        for pollutant in POLLUTANTS:

            fileName = "%s_%s.csv" % (country, pollutant)
            print(fileName)
            file_path = os.path.join(folder_out, dir, fileName)
            
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8-sig') as file:
                    print(file)
                    first_line = file.readline().strip()#.decode('utf-8')
                    
                    if not first_line.startswith('<!DOCTYPE html'): #first_line.startswith('network_countrycode'):
                    #print(fileName,'exist')

                        df_temp = pd.read_csv(file_path)
                        dfs.append(df_temp[df_columns])

    df_all = pd.concat(dfs, ignore_index=True)
    print ('Dataframe assembled')
    return df_all

# Update the final dataset
def update_dataset(new_df, folder_out = 'data', fileName = "se4g_pollution_dataset.csv"):

    full_path = os.path.join(folder_out, fileName)

    if os.path.isfile(full_path):
        # Open the CSV dataset
        df = pd.read_csv(full_path)
        df['value_datetime_begin'] = pd.to_datetime(df['value_datetime_begin'])
        new_df['value_datetime_begin'] = pd.to_datetime(new_df['value_datetime_begin'])

        # Filter rows from new_df based on the datetime
        filtered_rows = new_df[new_df['value_datetime_begin'] > df['value_datetime_begin'].max()]
        if filtered_rows.empty:
            print("Nothing to update inside dataset ->",fileName)
        elif not filtered_rows.empty:
            # Update the dataset by adding the filtered rows
            updated_df = pd.concat([df, filtered_rows], ignore_index=True)
            updated_df = updated_df.sort_values(by='value_datetime_begin')
            # Save the updated dataset
            updated_df.to_csv(full_path, index=False)
            print("Dataset ->",fileName," updated successfully")

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
    df['month_day'] = datetime_objects.dt.strftime('%m%d')
    #df['value_datetime_begin'] = pd.to_datetime(df['value_datetime_begin']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Compute daily mean of 'value_numeric' for each 'pollutant' and 'network_countrycode'
    daily_mean = df.groupby(['pollutant', 'network_countrycode', 'month_day'])['value_numeric'].mean().reset_index()
    
    # Merge the daily mean back to the original dataframe
    df = df.merge(daily_mean, on=['pollutant', 'network_countrycode', 'month_day'], suffixes=('', '_mean'))

    df['country'] = df['network_countrycode'].map(country)
    df = df[['pollutant', 'country', 'month_day', 'value_numeric_mean']].copy()

    df = df.drop_duplicates().reset_index(drop=True)
    
    
    if os.path.isfile(full_path):
        old_df = pd.read_csv(full_path)
        
        #print(df['month_day'].max().dtype)
        filtered_rows = df[df['month_day'].astype('int64') > old_df['month_day'].max()]
        
        filtered_rows = filtered_rows.dropna()
        if filtered_rows.empty:
            
            print("Nothing to update inside dataset ->",fileName)
        elif not filtered_rows.empty:
            updated_df = pd.concat([old_df, filtered_rows], ignore_index=True)
            updated_df = updated_df.sort_values(by=['month_day', 'country', 'pollutant'])
            updated_df.to_csv(full_path, index=False)
            print("Dataset ->",fileName," updated successfully")
    else: 
         df.to_csv(full_path, index=False)
         print("Dataset ->",fileName," created successfully")
        
#---------------------------------------------------------------------------------------------------------------------#

     
def update_data():
    if Login().logged_in:
        # Download and get the dataframe file name
        dir = download_request(folder_out = 'data_prova')
        #dir = '2023-06-09_14_50_48'

        # Build the dataframe with the required structure
        df = build_dataframe(dir, folder_out = 'data_prova')

        # Update the main dataset & the dashboard dataset 
        new_df = update_dataset(df, folder_out = 'data_prova')
        update_dashboard_dataset(df, folder_out = 'data_prova')

        # Update DB

        download_DB( conn=connect_right_now() )
        
        # Update dashboard table
        update_dashboard_table( conn=connect_right_now(), 
                                engine=connect_with_sqlalchemy()
                                )
    else:
        print("You need to be logged in to access this feature.")
    '''filtered_rows = update_DB_from_CSV(df, conn, conn, table_name = 'se4g_pollution') # new_df
    update_dashboard_DB_from_CSV(filtered_rows, conn, conn, table_name = 'se4g_dashboard')
    conn.close()'''   


def logged_in_example():
    if Login().logged_in:
        print('congratulations! You are logged in!')
    else:
        print("You need to be logged in to access this feature.")
   



	
#---------------------------------------------------------------------------------------------------------------------#



#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
#--                                                                                                                 --#
#--                     <<<<<<               USER LOGIN & REGISTRATION                    >>>>>>                    --#
#--                                                                                                                 --#
#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

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
    
    def _new_user(self):
        rgstr_usr = input('Insert your username: ')
        rgstr_psw = input('Insert your password: ')
        self.register_list[rgstr_usr] = rgstr_psw
        self.save_registrations_to_csv()
    
    def remove_registration(self, username, password):
        #self.register_list = [(u, p) for u, p in self.register_list if (u, p) != (username, password)]
        if username in self.register_list and self.register_list[username] == password:
            del self.register_list[username]
            self.save_registrations_to_csv()
    
    def _review_registrations(self):
        def approve_user(username, password):
            self.login._new_user(username, password)
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


class Login:
    def __init__(self):
        folder = 'data'
        filename = 'admins.csv'
        self.path_file = os.path.join(folder, filename)
        if os.path.isfile(self.path_file):
            df = pd.read_csv(self.path_file)
            self.user_list = dict(zip(df['Username'], df['Password']))
        self.logged_in = False

    def authenticate(self):
        # Add code for the login process
        self.logged_in = True

    def logout(self):
        # Add code for the logout process
        self.logged_in = False

    def check_credentials(self, username, password):
        if username in self.user_list and self.user_list[username] == password:
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
        df.to_csv(self.path_file, index=False)
        print(f"User data saved to {self.path_file} successfully.")

    def _to_DB(self):
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

            if self.check_credentials(username, password):
                conn = connect_right_now()
                return conn
            else:
                print("Invalid username or password.")

        login_button.on_click(handle_login_button_click)

    def _required(self):
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

            if self.check_credentials(username, password):
                self.logged_in = True
                print("Login successful!")
                # Perform the desired actions here after successful login
            else:
                print("Invalid username or password.")

        login_button.on_click(handle_login_button_click)

def login_register_section():
    register = Register()
    login = Login()
    if login.logged_in:
        print("You are logged in.")
        action = input("Choose an action (1 - Logout, 2 - Perform Authorized Action, 3 - Exit): ")

        if action == "1":
            login.logout()
            print("Logged out successfully.")
        elif action == "2":
            # Include code for authorized functions/cells
            print("Performing authorized action...")
        elif action == "3":
            print("Exiting...")
        else:
            print("Invalid action.")
    else:
        print("You are not logged in.")
        action = input("Choose an action (1 - Login, 2 - Register, 3 - Exit): ")

        if action == "1":
            login._required()
        elif action == "2":
            register._new_user()
        elif action == "3":
            print("Exiting...")
        else:
            print("Invalid action.")

#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#
#--                                                                                                                 --#
#--                    <<<<<<              DASHBOARD CREATION & VISUALIZATION              >>>>>>                   --#
#--                                                                                                                 --#
#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#


def create_df_from_table(table_name,conn=None):
    if conn is None:
        conn = connect_right_now()
    cursor = conn.cursor()

    # Generate the SQL statement to select data from the source table
    select_data_query = f"SELECT * FROM {table_name};"

    # Execute the SELECT command
    cursor.execute(select_data_query)

    columns = [desc[0] for desc in cursor.description]

    # Fetch all the rows
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Create a pandas DataFrame from the fetched rows
    df = pd.DataFrame(rows, columns=columns)
    #print(f'df {table_name} created')
    return df


class DescriptiveStats:
    def __init__(self):
        self.df_pollutant = create_df_from_table(table_name='pollutant_detection')
        self.df_station = create_df_from_table(table_name='station')
        
        # Dropdown widgets for country and pollutant selection
        self.country_dropdown = widgets.Dropdown(
            options=self.df_station['network_countrycode'].unique(),
            description='Country:'
        )

        self.pollutant_dropdown = widgets.Dropdown(
            description='Pollutant:'
        )

        # Text widget to display statistics
        self.statistics_text = widgets.Textarea(
            description='Statistics:',
            disabled=True,
            layout={'width': '500px', 'height': '200px'}
        )

        # Event listeners for dropdown selection
        self.country_dropdown.observe(self.update_pollutants, 'value')
        self.pollutant_dropdown.observe(self.update_statistics, 'value')

        # Display widgets
        display(self.country_dropdown)
        display(self.pollutant_dropdown)
        display(self.statistics_text)

    def create_df_from_table(self, table_name):
        # Implementation to create DataFrame from table
        # ...
        pass

    def update_pollutants(self, change):
        country = self.country_dropdown.value

        if country:
            pollutants = self.df_pollutant[self.df_pollutant['station_code'].isin(
                self.df_station[self.df_station['network_countrycode'] == country]['station_code'])]['pollutant'].unique()
            self.pollutant_dropdown.options = pollutants
            self.pollutant_dropdown.disabled = False
        else:
            self.pollutant_dropdown.options = []
            self.pollutant_dropdown.disabled = True

    def update_statistics(self, change):
        country = self.country_dropdown.value
        pollutant = self.pollutant_dropdown.value

        filtered_df = self.df_pollutant.merge(self.df_station, on='station_code')
        filtered_df = filtered_df[(filtered_df['network_countrycode'] == country) & (filtered_df['pollutant'] == pollutant)]

        mean_value = filtered_df['value_numeric'].mean()
        max_value = filtered_df['value_numeric'].max()
        min_value = filtered_df['value_numeric'].min()

        self.statistics_text.value = f"Mean: {mean_value:.2f}\nMax: {max_value}\nMin: {min_value}"

        # Update the plot
        self.plot_statistics()

    def plot_statistics(self):
        country = self.country_dropdown.value
        pollutant = self.pollutant_dropdown.value

        filtered_df = self.df_pollutant.merge(self.df_station, on='station_code')
        filtered_df = filtered_df[(filtered_df['network_countrycode'] == country) & (filtered_df['pollutant'] == pollutant)]

        mean_value = filtered_df['value_numeric'].mean()
        max_value = filtered_df['value_numeric'].max()
        min_value = filtered_df['value_numeric'].min()

        self.statistics_text.value = f"Mean: {mean_value:.2f}\nMax: {max_value}\nMin: {min_value}"

        # Create a bar plot of the statistics
        stats = [mean_value, max_value, min_value]
        labels = ['Mean', 'Max', 'Min']

        plt.figure(figsize=(8, 6))
        plt.bar(labels, stats)
        plt.xlabel('Statistic')
        plt.ylabel('Value')
        plt.title(f'Statistics for {pollutant} in {country}')
        plt.show()



class FoliumMap:
    def __init__(self, table_name='se4g_pollution_main', db_columns='value_numeric, samplingpoint_x, samplingpoint_y'):
        self.table_name = table_name
        self.db_columns = db_columns
        self.selected_pollutant = None
        self.selected_datetime = None
        
    def get_columns(self, table_name_clmns='se4g_pollution_main', db_columns='value_datetime_end'):
        conn = connect_right_now()
        cursor = conn.cursor()
    
        # Generate the SQL statement to select data from the source table
        select_data_query = f"SELECT DISTINCT {db_columns} FROM {table_name_clmns};"

        # Execute the SELECT command
        cursor.execute(select_data_query)

        clmns = [desc[0] for desc in cursor.description]
        # Fetch all the rows
        rows_clmns = cursor.fetchall()

        cursor.close()
        conn.close()

        return pd.DataFrame(rows_clmns, columns=clmns)
    
    def select_filters(self, pollutants=None, datetime_list=None):
        if pollutants is None:
            pollutants = ['SO2', 'NO', 'NO2', 'CO', 'PM10']
        if datetime_list is None:
            datetime_list = self.get_columns()['value_datetime_end'].tolist()

        pollutant_dropdown = widgets.Dropdown(
            options=pollutants,
            description='Select pollutant:'
        )
        datetime_dropdown = widgets.Dropdown(
            options=datetime_list,
            description='Select datetime:'
        )

        display(pollutant_dropdown)
        display(datetime_dropdown)

        self.selected_pollutant = pollutant_dropdown
        self.selected_datetime = datetime_dropdown

        return pollutant_dropdown, datetime_dropdown

    def update_maps(self, change):
        conn = connect_right_now()
        cursor = conn.cursor()

        # Generate the SQL statement to select data from the source table
        select_data_query = f"SELECT {self.db_columns} FROM {self.table_name} WHERE pollutant = '{self.selected_pollutant.value}' AND value_datetime_end = '{self.selected_datetime.value}';"

        # Execute the SELECT command
        cursor.execute(select_data_query)

        columns = [desc[0] for desc in cursor.description]
        # Fetch all the rows
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=columns)

        geom_list = [Point(xy) for xy in zip(df['samplingpoint_x'], df['samplingpoint_y'])]
        crs = 'epsg:4979'
        gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geom_list)

        # Update the MARKER MAP
        m_folium = folium.Map(location=[57, 15], zoom_start=2.5, tiles='CartoDB positron')

        for index, row in gdf.iterrows():
            folium.Marker(
                location=[row['geometry'].y, row['geometry'].x], 
                popup=row['value_numeric'],
                icon=folium.map.Icon(color='red')
            ).add_to(m_folium)

        # Update the HEAT MAP
        m_heat = folium.Map(location=[55, 15], tiles='Cartodb dark_matter', zoom_start=2.5)

        heat_data = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry]

        plugins.HeatMap(heat_data).add_to(m_heat)

        # Update the legend HTML content
        pollutant_selected = self.selected_pollutant.value
        datetime_formatted = pd.to_datetime(self.selected_datetime.value).strftime('%y-%m-%d %H:%M')
        legend_html = f"<div style='position:fixed; top:10px; left:10px; background-color:white; padding:5px; border:1px solid gray; z-index:9999; font-size:12px;'>" \
                      f"<b>Selected Filters:</b><br>" \
                      f"Pollutant: {pollutant_selected}<br>" \
                      f"Datetime: {datetime_formatted}" \
                      f"</div>"

        # Clear previous legend and add the updated legend to the map
        m_folium.get_root().html.children = []
        m_folium.get_root().html.add_child(folium.Element(legend_html))

        # Clear previous legend and add the updated legend to the map
        m_heat.get_root().html.children = []
        m_heat.get_root().html.add_child(folium.Element(legend_html))

        # Display the updated maps
        display(m_folium)
        display(m_heat)
        




def load_data(table_name):
    # Connect to the database and fetch the data
    conn = connect_right_now()
    cursor = conn.cursor()

    # Generate the SQL statement to select data from the source table
    select_data_query = f"SELECT * FROM {table_name};"

    # Execute the SELECT command
    cursor.execute(select_data_query)

    columns = [desc[0] for desc in cursor.description]

    # Fetch all the rows
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Create a pandas DataFrame from the fetched rows
    df = pd.DataFrame(rows, columns=columns)

    unique_month_day = df['month_day'].unique()
    month_day_dict = {day: index + 1 for index, day in enumerate(unique_month_day)}

    df['time_series'] = df['month_day'].map(month_day_dict)
    df = df[df['country'] != 'Bosnia and Herzegovina']

    df['month_day_date'] = '2023' + df['month_day'].astype(str)
    df['month_day_date'] = pd.to_datetime(df['month_day_date'], format='%Y%m%d')

    return df

class Dashboard:
    def __init__(self, table_name='se4g_dashboard'):
        self.app = JupyterDash(__name__)
        self.df = load_data(table_name)  # Initialize an empty DataFrame

    def load_data(self):
        # Connect to the database and fetch the data
        conn = connect_right_now()
        cursor = conn.cursor()

        # Generate the SQL statement to select data from the source table
        select_data_query = f"SELECT * FROM {self.table_name};"

        # Execute the SELECT command
        cursor.execute(select_data_query)

        columns = [desc[0] for desc in cursor.description]

        # Fetch all the rows
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Create a pandas DataFrame from the fetched rows
        self.df = pd.DataFrame(rows, columns=columns)

        unique_month_day = self.df['month_day'].unique()
        month_day_dict = {day: index + 1 for index, day in enumerate(unique_month_day)}

        self.df['time_series'] = self.df['month_day'].map(month_day_dict)
        self.df = self.df[self.df['country'] != 'Bosnia and Herzegovina']

        self.df['month_day_date'] = '2023' + self.df['month_day'].astype(str)
        self.df['month_day_date'] = pd.to_datetime(self.df['month_day_date'], format='%Y%m%d')

    def create_dashboard(self):
        available_indicators = self.df['pollutant'].unique()

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        self.app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

        self.app.layout = html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='crossfilter-xaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='SO2'
                    ),
                    dcc.RadioItems(
                        id='crossfilter-xaxis-type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ],
                    style={'width': '49%', 'display': 'inline-block'}),

                html.Div([
                    dcc.Dropdown(
                        id='crossfilter-yaxis-column',
                        options=[{'label': i, 'value': i} for i in available_indicators],
                        value='CO'
                    ),
                    dcc.RadioItems(
                        id='crossfilter-yaxis-type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
            ], style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'
            }),

            html.Div([
                dcc.Graph(
                    id='crossfilter-indicator-scatter',
                    hoverData={'points': [{'customdata': 'Andorra'}]}
                )
            ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
            html.Div([
                dcc.Graph(id='x-time-series'),
                dcc.Graph(id='y-time-series'),
            ], style={'display': 'inline-block', 'width': '49%'}),

            html.Div(dcc.Slider(
                id='crossfilter-year--slider',
                min=self.df['time_series'].min(),
                max=self.df['time_series'].max(),
                value=self.df['time_series'].max(),
                marks={str(time): str(time) for time in self.df['month_day_date'].unique()},
                step=None
            ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
        ])

        @self.app.callback(
            dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
            [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
             dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
             dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
             dash.dependencies.Input('crossfilter-yaxis-type', 'value'),
             dash.dependencies.Input('crossfilter-year--slider', 'value')])
        def update_graph(xaxis_column_name, yaxis_column_name,
                         xaxis_type, yaxis_type,
                         year_value):
            dff = self.df[self.df['time_series'] == year_value]

            return {
                'data': [dict(
                    x=dff[dff['pollutant'] == xaxis_column_name]['value_numeric_mean'],
                    y=dff[dff['pollutant'] == yaxis_column_name]['value_numeric_mean'],
                    text=dff[dff['pollutant'] == yaxis_column_name]['country'],
                    customdata=dff[dff['pollutant'] == yaxis_column_name]['country'],
                    mode='markers',
                    marker={
                        'size': 25,
                        'opacity': 0.7,
                        'color': 'orange',
                        'line': {'width': 2, 'color': 'purple'}
                    }
                )],
                'layout': dict(
                    xaxis={
                        'title': xaxis_column_name,
                        'type': 'linear' if xaxis_type == 'Linear' else 'log'
                    },
                    yaxis={
                        'title': yaxis_column_name,
                        'type': 'linear' if yaxis_type == 'Linear' else 'log'
                    },
                    margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
                    height=450,
                    hovermode='closest'
                )
            }


        def create_time_series(dff, axis_type, title):
            return {
                'data': [dict(
                    x=dff['time_series'],
                    y=dff['value_numeric_mean'],
                    mode='lines+markers'
                )],
                'layout': {
                    'height': 225,
                    'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
                    'annotations': [{
                        'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                        'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                        'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                        'text': title
                    }],
                    'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
                    'xaxis': {'showgrid': False}
                }
            }

        @self.app.callback(
            dash.dependencies.Output('x-time-series', 'figure'),
            [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
             dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
             dash.dependencies.Input('crossfilter-xaxis-type', 'value')])
        def update_x_timeseries(hoverData, xaxis_column_name, axis_type):
            country_name = hoverData['points'][0]['customdata']
            dff = self.df[self.df['country'] == country_name]
            dff = dff[dff['pollutant'] == xaxis_column_name]
            title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
            return create_time_series(dff, axis_type, title)

        @self.app.callback(
            dash.dependencies.Output('y-time-series', 'figure'),
            [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
             dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
             dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
        def update_y_timeseries(hoverData, yaxis_column_name, axis_type):
            dff = self.df[self.df['country'] == hoverData['points'][0]['customdata']]
            dff = dff[dff['pollutant'] == yaxis_column_name]
            return create_time_series(dff, axis_type, yaxis_column_name)
    
    def run(self):
        #self.load_data()
        self.create_dashboard()  # Set up the layout of the application
        self.app.run_server(mode='inline')  # Change mode to 'external' if using Jupyter Notebook






class Interactive:
    def __init__(self, 
                    df_pollutant=create_df_from_table(table_name = 'pollutant_detection'), 
                    df_station=create_df_from_table(table_name = 'station')):
        self.df_pollutant = df_pollutant
        self.df_station = df_station

    def select_pollutant(self):
        pollutants = self.df_pollutant['pollutant'].unique()
        dropdown_pollutant = widgets.Dropdown(
            options=pollutants,
            description='Select pollutant:',
            layout=widgets.Layout(width='250px'),
            style={'description_width': 'initial', 'min-width': '250px', 'font-size': '10pt'}
        )
        display(dropdown_pollutant)
        return dropdown_pollutant

    def select_date(self):
        self.df_pollutant['value_datetime_begin'] = pd.to_datetime(self.df_pollutant['value_datetime_begin'])
        dates = self.df_pollutant['value_datetime_begin'].dt.date.unique()
        dropdown_date = widgets.Dropdown(
            options=dates,
            description='Select date:',
            layout=widgets.Layout(width='250px'),
            style={'description_width': 'initial', 'min-width': '250px', 'font-size': '10pt'}
        )
        display(dropdown_date)
        return dropdown_date

    def create_bokeh_plot(self, selected_pollutant, selected_date):
        df_selected = self.df_pollutant[
            (self.df_pollutant['pollutant'] == selected_pollutant) &
            (self.df_pollutant['value_datetime_begin'].dt.date == selected_date)
        ]

        # Merge the station and df_pollutant DataFrames on station_code
        df_country = pd.merge(self.df_station, df_selected, on='station_code')

        countries = df_country['network_countrycode'].unique()
        colors = Category10[10][:len(countries)]

        p = figure(x_axis_type='datetime', title=f"Pollutant: {selected_pollutant} - Date: {selected_date}",
                   width=800, height=400)

        for country, color in zip(countries, colors):
            df_filtered = df_country[df_country['network_countrycode'] == country]
            df_filtered = df_filtered.sort_values('value_datetime_begin')  # Sort by 'value_datetime_begin'
            source = ColumnDataSource(df_filtered)
            p.line(x='value_datetime_begin', y='value_numeric', source=source, line_color=color,
                   legend_label=country)

        p.legend.location = "top_left"
        p.legend.click_policy = "hide"

        output_notebook()
        show(p)
