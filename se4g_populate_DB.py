from se4g_helper import download_DB, connect_right_now
conn = connect_right_now()

download_DB(connection=conn)

conn.close()