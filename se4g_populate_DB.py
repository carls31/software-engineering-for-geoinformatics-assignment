from se4g_helper import (download_DB, update_dashboard_table, 
                         connect_right_now, connect_with_sqlalchemy)
download_DB( conn=connect_right_now() )
 
# Update dashboard table
update_dashboard_table( conn=connect_right_now(), 
                        engine=connect_with_sqlalchemy()
                        )