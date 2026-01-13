FROM python:3.12

ADD plugin.py requirements.txt /usr/local/bin/

RUN pip install -r /usr/local/bin/requirements.txt

ENTRYPOINT python /usr/local/bin/plugin.py
