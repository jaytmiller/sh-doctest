FROM python:3.11-bullseye

COPY requirements.txt /requirements.txt
RUN  pip install -r /requirements.txt
COPY sh_doctest /sh_doctest
COPY specs /specs
