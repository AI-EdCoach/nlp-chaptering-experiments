FROM python:3.10

RUN apt-get update && apt-get install  -y \
    ffmpeg \
    libsm6 \
    libxext6 
WORKDIR /home/MLServiceProj

COPY requirements.txt requirements.txt
COPY worker_requirements.txt worker_requirements.txt
RUN pip3.10 install -r requirements.txt
RUN pip3.10 install -r worker_requirements.txt

# COPY . /home/MLServiceProj