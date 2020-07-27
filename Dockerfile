FROM python:3-alpine

WORKDIR /focus

ADD . /focus


RUN pip3 install -r requirements.txt

CMD [ "python3", "./pcpe_metrics_collector.py" ]
