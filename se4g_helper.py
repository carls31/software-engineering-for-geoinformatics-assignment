import os
import requests
import pandas as pd
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display

#import codecs


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
        print('connected with ',ip, ' through psycopg2')
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
        print('connected with ',ip, ' through sqlalchemy')
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
    '''filtered_rows = update_DB_from_CSV(df, conn, conn, table_name = 'se4g_pollution') # new_df
    update_dashboard_DB_from_CSV(filtered_rows, conn, conn, table_name = 'se4g_dashboard')
    conn.close()'''   

	
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
                print("Login successful!")
                # Perform the desired actions here after successful login
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


def create_df_from_table(table_name='pollutant_detection',conn=None):
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
    print(f'df {table_name} created')
    return df


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
    print(f'df {table_name} created')
    return df