# SE4GEO Project
**Project Assignment of the course "Software Engineering for Geoinformatics" at Politecnico di Milano.**

We have included a brief overview of the functionality and usage of our project below. It is an Open-Source Web Application designed to provide users with valuable information on air pollution and pollutants of the cities in Europe. Our main goal is to create an open and collaborative platform where users can actively contribute to data enrichment, the implementation of new functionalities, and the development of custom models.

### Installation
This tutorial required Anaconda or mamba being installed. After cloning the repository, set up the python environment using the command:
```sh
conda env create -f se4g.yml
```
Or fork the repository for having your own copy. The main modules depends on [botorch](https://botorch.org/) and [pytorch](https://pytorch.org/).
### Requirements 
This RASD (Requirement Analysis and Specification Document)document outlines the requirements for the development of an interactive client-server application that allows users to access, query, and visualize air quality data from public digital archives. The system consists of a database for storing data, a web server for querying the database, and a dashboard for requesting, processing, and visualizing data.The requirements include non-functional aspects such as language support, availability, and user-friendly interface, as well as functional aspects like data access, processing, scalability, and security.
### Design 
The introduction section starts by emphasizing the importance of having a clear understanding of the design goals before implementing a software project. The purpose of the document is to outline the architecture and functionality of the web application, which enables users to access, query, and visualize air quality data retrieved from public digital archives. It concludes with a mention of the Database Design and REST APIs sections, which are part of the Software Design. The Database Design involves utilizing data obtained from the API of cities and managing it using a PostgreSQL database. The REST APIs are implemented using Flask, a Python web framework, to handle user requests and interact with the web server.
     
The main functions and the dashboard are included in the folder:
 * helper
 * 
The dashboard is enclosed in the file:
  * se4g_JupyterDash_demo.ipynb
  
The documents are contained within the:
 * GRUPPO_GEO_RASD.pdf
 * GRUPPO_GEO-DD.pdf
## 2.2 HOW TO RUN THE APPLICATION
The project aims to be open-source, allowing it to remain constantly updated. The platform, represented by a notebook transformed into a dashboard, serves as the main interface for users.
1. Select the type of user. You can decide between:
* GEO User: This is an Environmental Engineer who, in addition to having access to the dashboard, can also download existing data and, most importantly, upload new data. This user has the ability to contribute to the enrichment of available data.
* MTM User: This profile is dedicated to Mathematical Engineers or professionals such as Data Scientists who can use the dashboard to visualize available data and develop numerical, computational, or statistical models. This user has the ability to utilize the data for analysis and the development of custom models.
 
* :warning:  default basic profile will be available that does not require registration, allowing users to access the dashboard without further formalities.

2. Select a city in Europe of which you want to retrieve data

