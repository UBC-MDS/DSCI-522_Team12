# Docker file for the customer complaint analyzer project
# Luke Yang, Dec, 2022

# use jupyter/datascience-notebook as the base image 
FROM jupyter/datascience-notebook

USER root

RUN sudo apt-get update
# install the required packages
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
    vl-convert-python

RUN export QUARTO_VERSION="1.2.262"


# RUN mkdir -p /opt/quarto/${QUARTO_VERSION}

# RUN curl -o quarto.tar.gz -L \
#     "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"

RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb
# RUN sudo tar -zxvf quarto.tar.gz \
#     -C "/opt/quarto/${QUARTO_VERSION}" \
#     --strip-components=1
RUN sudo apt-get install gdebi-core -y

RUN gdebi --non-interactive quarto-linux-amd64.deb

RUN quarto check
# RUN rm quarto.tar.gz
# RUN ln -s /opt/quarto/${QUARTO_VERSION}/bin/quarto /usr/local/bin/quarto