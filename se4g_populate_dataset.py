from se4g_helper import download_request, build_dataframe, update_dataset, update_dashboard_dataset
# Download and get the dataframe file name
#dir = download_request(folder_out = 'data_prova')
dir = '04-06-2023_20_37_01'

# Build the dataframe with the required structure
df = build_dataframe(dir, folder_out = 'data_prova')

# Update the main dataset & the dashboard dataset 
new_df = update_dataset(df, folder_out = 'data_prova')
update_dashboard_dataset(df, folder_out = 'data_prova')


# Update DBs 
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
print('connected with ',ip)

filtered_rows = update_DB_from_CSV(new_df, conn, table_name = 'se4g_pollution')
update_dashboard_DB_from_CSV(filtered_rows, conn, table_name = 'se4g_dashboard')

conn.close()