FROM python:3.10

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
WORKDIR /home/MLServiceProj

COPY requirements.txt requirements.txt
RUN pip3.10 install -r requirements.txt

COPY . /home/MLServiceProj