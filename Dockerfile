FROM python:3.7

#ADD environment.yml /tmp/environment.yml
ADD requirements.txt /app/requirements.txt
ADD requirements_before.txt /app/requirements_before.txt
ADD dev_requirements.txt /app/dev_requirements.txt

RUN apt update && apt install -y libpq-dev gdal-bin libgdal-dev
#RUN apt-get install libgdal-dev

#RUN apt-get update && apt-get install -y build-essential \
#libpq-dev python3-dev \
#libspatialindex-dev python-rtree \
#libopenjp2-7-dev

#RUN conda env create -f /tmp/environment.yml

#RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
#ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH
#SHELL ["conda", "run", "-n", "InVEST", "/bin/bash", "-c"]

WORKDIR /app
RUN pip install -r requirements_before.txt
RUN pip install -r requirements.txt
RUN pip install -r dev_requirements.txt

COPY . /app
ADD geoprocessing.py /usr/local/lib/python3.7/site-packages/pygeoprocessing/geoprocessing.py
RUN chmod +x startup.py
RUN chmod +x api.py

#RUN \
# apk add --no-cache postgresql-libs && \
# apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
# pip install -r requirements.txt --no-cache-dir && \
# apk --purge del .build-deps


# CMD ["python", "startup.py"]
CMD ["gunicorn", "-t", "600",  "--log-level", "info", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "api:app"]

#EXPOSE 8000

#CMD ["conda", "run", "-n", "InVEST", "python", "startup.py"]
#ENTRYPOINT ["python", "startup.py"]