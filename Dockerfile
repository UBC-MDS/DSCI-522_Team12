# Docker file for the customer complaint analyzer project
# Luke Yang, Dec 9, 2022

# use jupyter/datascience-notebook as the base image 
FROM jupyter/datascience-notebook

USER root

# ensure packages are up to date on the system
RUN sudo apt-get update

# install the required ptyhon packages
RUN pip install altair==4.2.0\
    docopt==0.6.2\
    numpy==1.23.5\
    pandas==1.4.4\
    pytest==7.2.0\
    requests==2.28.1\
    scikit-learn==1.1.3\
    docopt-ng==0.8.1\
    altair_data_server==0.4.1\
    altair_saver==0.5.0\
    selenium==4.2.0\
    vl-convert-python==0.4.0

# install quarto 

# pull quarto from website
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb

RUN sudo apt-get install gdebi-core -y

RUN gdebi --non-interactive quarto-linux-amd64.deb

# check quarto install worked correctly
RUN quarto check

RUN sudo apt-get install lmodern
