from se4g_helper import download_DB, connect_right_now
conn = connect_right_now()

download_DB(connection=conn,table_name='se4g_pollution_main')

conn.close()