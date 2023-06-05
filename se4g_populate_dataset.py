from se4g_helper import download_request, build_dataframe, update_dataset, update_dashboard_dataset
# Download and get the dataframe file name
dir = download_request(folder_out = 'data_prova')
#dir = '05-06-2023_10_25_47'

# Build the dataframe with the required structure
df = build_dataframe(dir, folder_out = 'data_prova')

# Update the main dataset & the dashboard dataset 
new_df = update_dataset(df, folder_out = 'data_prova')
update_dashboard_dataset(df, folder_out = 'data_prova')

 # Connect to DB
from se4g_helper import update_DB_from_CSV, update_dashboard_DB_from_CSV
import psycopg2
ip = '192.168.30.19'
ip = 'localhost'
conn = psycopg2.connect(
    host = ip,
    database = "se4g",
    user = "postgres",
    password = "carIs3198"
)
print('connected with psycopg2 in',ip)
from sqlalchemy import create_engine
file = 'bin.txt'
with open('code/'+file, 'r') as f:
    engine = create_engine('postgresql://postgres:'+f.read()+'@'+ip+':5432/se4g') 
con = engine.connect()
print('connected with SQLAlchemy in',ip)

# Update DB
filtered_rows = update_DB_from_CSV(new_df, conn,engine, table_name = 'se4g_pollution')
update_dashboard_DB_from_CSV(filtered_rows, conn,engine, table_name = 'se4g_dashboard')
conn.close()