FROM python:3.10

WORKDIR /home/MLServiceProj

COPY requirements.txt requirements.txt
RUN pip3.10 install -r requirements.txt

COPY . /home/MLServiceProj