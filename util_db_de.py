import ipywidgets as widgets
from IPython.display import display
from sqlalchemy import create_engine


def login():

    user = widgets.Text(
        #value='postgres',
        placeholder='Type postgres',
        description='Username:',
        disabled=False   
        )
    
    psw = widgets.Password(
            #value='password',
            placeholder='Enter password',
            description='Password:',
            disabled=False
        )
    return widgets.VBox([user, psw])


def login_required():
    user = widgets.Text(
        placeholder='Type postgres',
        description='Username:',
        disabled=False   
    )

    psw = widgets.Password(
        placeholder='Enter password',
        description='Password:',
        disabled=False
    )
    
    login_button = widgets.Button(description="Login")
    display(user, psw, login_button)

    def handle_login_button_click(button):
        username = user.value
        password = psw.value

        # Check if username and password are valid
        if username == "postgres" and password == "carIs3198":
            # Connect to the database
            engine = create_engine('postgresql://'+username+':'+password+'@localhost:5432/se4g') 
            con = engine.connect()
            # Perform any necessary database operations
            # ...
            # Return the database connection or perform any other actions
            print('connected with localhost')
            return con
        else:
            print('it does not work')

    login_button.on_click(handle_login_button_click)

