FROM --platform=linux/amd64 python:3.9-buster
 
# install dependencies

COPY . .

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip3 install -r requirements.txt
COPY . /opt/app
 
# start flask server - use gunicorn in production
CMD [ "gunicorn", "--bind" , "0.0.0.0:8080" , "app:app"]