from se4g_helper import (download_DB, connect_right_now,
                        connect_with_sqlalchemy, update_dashboard_table)
conn = connect_right_now()

download_DB(connection=conn,table_name='se4g_pollution_main')

'''conn.close() '''

'''dataset = 'se4g_dashboard_dataset.csv' # - 1.2s
folder = 'data_prova' '''

# Update dashboard table

'''conn = connect_right_now()'''
engine = connect_with_sqlalchemy()
update_dashboard_table()


conn.close()
engine.dispose()