FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends wget unzip build-essential libreadline-dev \
libncursesw5-dev libssl-dev libsqlite3-dev libgdbm-dev libbz2-dev liblzma-dev zlib1g-dev uuid-dev libffi-dev libdb-dev git

#wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && unzip chromedriver_linux64.zip
#wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
WORKDIR /usr/src

COPY . .

ENV DEBIAN_FRONTEND=noninteractive
RUN cp ./utils/chromedriver /usr/bin/chromedriver && chmod 755 /usr/bin/chromedriver
RUN apt-get install -y ./utils/google-chrome-stable_current_amd64.deb

RUN apt-get install -y python3.8 python3-pip

RUN pip install --no-cache-dir -r requirements.txt
