# SE4GEO Project
**Project Assignment of the course "Software Engineering for Geoinformatics" at Politecnico di Milano.**

This is an Open-Source Application designed to provide users with information on air pollution and pollutants of European cities. Our main goal is to create a collaborative platform where users can actively contribute to data enrichment, the implementation of new functionalities, and the development of custom models.

### Installation
The application required Anaconda or mamba being installed. After cloning the repository, set up the python environment using the command:
```sh
conda env create -f se4g.yml
```
Alternatively you could also consider to fork the repository for having your own copy. 
     
 and the dashboard are included in the folder:
 * The functions are defined inside: se4g_helper.py
 * The dashboard is enclosed in the file: se4g_JupyterDash_demo.ipynb

The documentations can be found:
 * GRUPPO_GEO_RASD.pdf
 * GRUPPO_GEO-DD.pdf
 
### How To Run
Login and go to 2. otherwise Register following the instructions in 1.
1. Select the user profile
     * GEO User: This is an Environmental Engineer who, in addition to having access to the dashboard, can also download existing data and, most importantly, upload new data. This user has the ability to contribute to the enrichment of available data.
     * MTM User: This profile is dedicated to Mathematical Engineers or professionals such as Data Scientists who can use the dashboard to visualize available data and develop numerical, computational, or statistical models. This user has the ability to utilize the data for analysis and the development of custom models.

     * :warning:  default basic profile will be available that does not require registration, allowing users to access the dashboard without further formalities.

Please wait for your registration request to be approved.

2. Select a city in Europe of which you want to retrieve data
 * dashboard daily mean
 * dashboard select day by user
 * histograms
 * select pollutant and shows timeseries of all the cities 
 * correlation matrix
