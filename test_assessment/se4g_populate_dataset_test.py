from se4g_helper import download_request, build_dataframe, update_dataset
import sys 

orig_stdout = sys.stdout
f = open('C:\Users\Utente\Documents\GitHub\SE4GEO-Lab/se4g_test.txt','w')
sys.stdout = f

directory = 'data_test'
print('output directory:',directory)

# Download and get the dataframe file name
dir = download_request(folder_out = directory)
print('dataframe folder:',dir)

# Build the dataframe with the required structure
df = build_dataframe(dir, folder_out = directory)
print('dataframe built:',df)

# Update the final dataset
update_dataset(df, folder_out = directory)

print('se4g_pollution_dataset updated successfully')

sys.stdout = orig_stdout
f.close()