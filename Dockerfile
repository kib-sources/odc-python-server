FROM python:3.9
ADD . /odc
WORKDIR /odc
RUN pip3 install -r requirements.txt
EXPOSE 5000