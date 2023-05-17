import ipywidgets as widgets
from sqlalchemy import create_engine, text


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


'''class user():
    def __init__(self,user,psw):
        self.user = user
        self.psw = psw

    def __call__(self):
        return self.user,self.psw
    
    def connect_to_db(self) :
        engine = create_engine('postgresql://'+self.user.value+':'+self.psw.value+'@localhost:5432/se4g') 
        con = engine.connect()
        print('connected with localhost')
        return con'''
