FROM jupyter/datascience-notebook:python-3.7.6

RUN git clone https://github.com/cannin/covid-sicr-test covid-sicr
WORKDIR covid-sicr

RUN pip install -e .
RUN python scripts/get-data.py
RUN python scripts/run.py SICRLMQC2R --n-warm=5 --n-iter=50
#RUN python scripts/visualize.py
RUN python scripts/get-n-data.py
RUN python scripts/make-tables.py
