import os
import pandas as pd
from se4g_helper import (download_request, build_dataframe, update_dataset, update_dashboard_dataset)
# Download and get the dataframe file name
dir = download_request(folder_out = 'data_prova')
#dir = '2023-06-09_14_50_48'

# Build the dataframe with the required structure
df = build_dataframe(dir, folder_out = 'data_prova')

# Update the main dataset & the dashboard dataset 
new_df = update_dataset(df, folder_out = 'data_prova')
update_dashboard_dataset(df, folder_out = 'data_prova')


# Update DB
'''filtered_rows = update_DB_from_CSV(df, conn, conn, table_name = 'se4g_pollution') # new_df
update_dashboard_DB_from_CSV(filtered_rows, conn, conn, table_name = 'se4g_dashboard')
conn.close()'''