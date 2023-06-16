<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

# SE4GEO Project
**Project Assignment of the course "Software Engineering for Geoinformatics" at Politecnico di Milano.**

This is an Open-Source Application designed to provide users with information on air pollution and pollutants of European cities. Our main goal is to create a collaborative platform where users can actively contribute to data enrichment, the implementation of new functionalities, and the development of custom models.

### Installation
The application required Anaconda or mamba being installed. After cloning the repository, set up the python environment using the command:
```sh
conda env create -f se4g.yml
```
Alternatively, you can fork the repository to have your own copy.

The main functions are defined in the file 'se4g_helper.py,' and the dashboard is included in 'se4g_JupyterDash_demo.ipynb'.

Documentation files:
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

Feel free to explore and utilize these features for your analysis and model development.
