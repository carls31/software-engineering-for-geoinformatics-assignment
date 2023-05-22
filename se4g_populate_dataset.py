from se4g_helper import download_request, build_dataframe, update_dataset

# Download and get the dataframe file name
dir = download_request(folder_out = 'data_prova')

# Build the dataframe with the required structure
df = build_dataframe(dir, folder_out = 'data_prova')

# Update the final dataset
update_dataset(df, folder_out = 'data_prova')

print('se4g_pollution_dataset updated successfully')