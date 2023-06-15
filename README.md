# SE4GEO Project
Project Assignment of the course "Software Engineering for Geoinformatics" at Politecnico di Milano during the academic year 2022/2023

Develop an interactive application for air quality monitoring

Public authorities collect air quality and weather observations in near-real time from ground
sensor stations and store them in digital archives. Generally, ground sensors data are
composed of long time series of observations and sensors metadata (including coordinates,
type of measured variable, etc.). Often, observations from different sensors and/or providers
require different patterns for data accessing, harmonization, and processing. To this end,
interactive applications and dashboards, capable of facilitating such tasks, are key for
supporting both public authorities as well as ordinary citizens in data processing and
visualization. The purpose of this project is to design and develop an interactive client-server
application to perform the above tasks.

The accompanying documentation can be located within this repository and provides a more comprehensive understanding of the software's scope, plan, purpose, testing, and implementation than a readme file ever could.
We have included a brief overview of the functionality and usage of our project below. It is an Open-Source Web Application designed to provide users with valuable information on air pollution and pollutants of the cities in Europe . Through the visualization of air quality data collected from sensors and additional analysis offered by the application, users gain access to comprehensive insights regarding air pollution.

The team of developers is composed by the following people:

       Lorenzo Carlassara
       Angelica Iseni
       Emma Lodetti
       Virginia Valeri


# 2.INSTRUCTIONS

## 2.1.DESCRIPTION OF THE FILES
First of all download all the folders and files that are inside the repository:
### Requirements 
This RASD (Requirement Analysis and Specification Document)document outlines the requirements for the development of an interactive client-server application that allows users to access, query, and visualize air quality data from public digital archives. The system consists of a database for storing data, a web server for querying the database, and a dashboard for requesting, processing, and visualizing data. The motivation behind this project is the European Commission's agreement to phase out gasoline and diesel cars by 2035, which requires monitoring and understanding air quality. The document provides an overview of the solution, including data harmonization, preprocessing, cleaning, descriptive statistics, and forecasting. It also lists the stakeholders, actors, domain assumptions, and various use cases. The requirements include non-functional aspects such as language support, availability, and user-friendly interface, as well as functional aspects like data access, processing, scalability, and security.

File:

-GRUPPO_GEO_RASD.pdf
### Design 
The introduction section starts by emphasizing the importance of having a clear understanding of the design goals before implementing a software project. The purpose of the document is to outline the architecture and functionality of the web application, which enables users to access, query, and visualize air quality data retrieved from public digital archives. It concludes with a mention of the Database Design and REST APIs sections, which are part of the Software Design. The Database Design involves utilizing data obtained from the API of cities and managing it using a PostgreSQL database. The REST APIs are implemented using Flask, a Python web framework, to handle user requests and interact with the web server.

This repository contains all the files needed in order to run the application:

-GRUPPO_GEO_DD.pdf

