import os
def set_the_working_directory():
    current_dir = os.getcwd()
    #print('Current directory: ',current_dir)
    parent_dir = os.path.dirname(current_dir)

    os.chdir(parent_dir)

    print('Current working directory:', os.getcwd())