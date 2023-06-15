# SE4GEO Project
Project Assignment of the course "Software Engineering for Geoinformatics" at Politecnico di Milano during the academic year 2022/2023

Develop an interactive application for air quality monitoring
# 1.INTRODUCTION
Public authorities collect air quality and weather observations in near-real time from ground
sensor stations and store them in digital archives. Generally, ground sensors data are
composed of long time series of observations and sensors metadata (including coordinates,
type of measured variable, etc.). Often, observations from different sensors and/or providers
require different patterns for data accessing, harmonization, and processing. To this end,
interactive applications and dashboards, capable of facilitating such tasks, are key for
supporting both public authorities as well as ordinary citizens in data processing and
visualization. The purpose of this project is to design and develop an interactive client-server
application to perform the above tasks.

We have included a brief overview of the functionality and usage of our project below. It is an Open-Source Web Application designed to provide users with valuable information on air pollution and pollutants of the cities in Europe . Through the visualization of air quality data collected from sensors and additional analysis offered by the application, users gain access to comprehensive insights regarding air pollution. Our main goal is to create an open and collaborative platform where users can actively contribute to data enrichment, the implementation of new functionalities, and the development of custom models.

The team of developers is composed by four M.Sc. Geoinformatics Engineering students:

       Lorenzo Carlassara
       Angelica Iseni
       Emma Lodetti
       Virginia Valeri


# 2.INSTRUCTIONS

## 2.1.DESCRIPTION OF THE FILES
First of all download all the folders and files that are inside the repository:
### Requirements 
This RASD (Requirement Analysis and Specification Document)document outlines the requirements for the development of an interactive client-server application that allows users to access, query, and visualize air quality data from public digital archives. The system consists of a database for storing data, a web server for querying the database, and a dashboard for requesting, processing, and visualizing data. The motivation behind this project is the European Commission's agreement to phase out gasoline and diesel cars by 2035, which requires monitoring and understanding air quality. The document provides an overview of the solution, including data harmonization, preprocessing, cleaning, descriptive statistics, and forecasting. It also lists the stakeholders, actors, domain assumptions, and various use cases. The requirements include non-functional aspects such as language support, availability, and user-friendly interface, as well as functional aspects like data access, processing, scalability, and security.

Download the file:
* GRUPPO_GEO_RASD.pdf
### Design 
The introduction section starts by emphasizing the importance of having a clear understanding of the design goals before implementing a software project. The purpose of the document is to outline the architecture and functionality of the web application, which enables users to access, query, and visualize air quality data retrieved from public digital archives. It concludes with a mention of the Database Design and REST APIs sections, which are part of the Software Design. The Database Design involves utilizing data obtained from the API of cities and managing it using a PostgreSQL database. The REST APIs are implemented using Flask, a Python web framework, to handle user requests and interact with the web server.
The document can be found in this file:
* GRUPPO_GEO_DD.pdf

You need to have an Anaconda environment with the following libraries installed:
    
       - flask
       - geopandas 
       - sqlalchemy
       - psycoppg2
       - json
       - pandas
     

This repository contains all the files needed in order to run the application:
* helper(all folders)
* se4g_helper.py (essential components for ensuring the functionality of the application)

## 2.2 HOW TO RUN THE APPLICATION
The project aims to be open-source, allowing it to remain constantly updated. The platform, represented by a notebook transformed into a dashboard, serves as the main interface for users.
1. Select the type of user. You can decide between:
* GEO User: This is an Environmental Engineer who, in addition to having access to the dashboard, can also download existing data and, most importantly, upload new data. This user has the ability to contribute to the enrichment of available data.
* CS User: This profile is intended for Computer Engineers or professionals such as Software Developers who can access the source code to implement new functionalities. They are actively able to contribute to the project's evolution.
* MTM User: This profile is dedicated to Mathematical Engineers or professionals such as Data Scientists who can use the dashboard to visualize available data and develop numerical, computational, or statistical models. This user has the ability to utilize the data for analysis and the development of custom models.
 
:warning:At the same time, a default basic profile will be available that does not require registration, allowing users to access the dashboard without further formalities.

2. Select a city in Europe of which you want to retrieve data

