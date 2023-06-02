from se4g_helper import download_request, build_dataframe, update_dataset, update_dashboard_dataset
# Download and get the dataframe file name
dir = download_request(folder_out = 'data_prova')

# Build the dataframe with the required structure
df = build_dataframe(dir, folder_out = 'data_prova')

# Update the main dataset & the dashboard dataset 
new_df = update_dataset(df, folder_out = 'data_prova')
update_dashboard_dataset(df, folder_out = 'data_prova')



# Update DBs 
#filtered_rows = update_DB(new_df, con, table_name = 'se4g_pollution')
#update_dashboard_DB(filtered_rows, con, table_name = 'se4g_dashboard')