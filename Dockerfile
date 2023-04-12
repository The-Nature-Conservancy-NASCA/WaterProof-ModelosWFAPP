FROM python:3.8.12-buster
#FROM python:3.7-buster

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /app/requirements.txt
ADD requirements_before.txt /app/requirements_before.txt
ADD dev_requirements.txt /app/dev_requirements.txt

RUN pip install --upgrade pip
RUN apt update && apt install -y libpq-dev gdal-bin libgdal-dev
RUN apt install -y gfortran
RUN apt-get install -y libspatialindex-dev


RUN pip install -r requirements_before.txt
RUN pip install -r requirements.txt
RUN pip install -r dev_requirements.txt

COPY . /app
ADD geoprocessing.py /usr/local/lib/python3.8/site-packages/pygeoprocessing/geoprocessing.py
RUN chmod +x startup.py
RUN chmod +x api.py


# CMD ["python", "startup.py"]
# CMD ["gunicorn", "-t", "600",  "--log-file", "-", "--bind", "0.0.0.0:8000", "--workers", "3", "-k", "uvicorn.workers.UvicornWorker", "api:app"]
# CMD ["gunicorn", "-t", "600",  "--log-level", "info", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "api:app"]

#EXPOSE 8000
