from se4g_helper import download_DB
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

download_DB(connection=conn)


conn.close()