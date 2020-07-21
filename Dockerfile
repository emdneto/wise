FROM python:3-alpine

ADD core/pcpe_metrics_collector.py /
ADD requirements.txt /

RUN pip3 install virtualenv
RUN pip3 install -r requirements.txt
RUN pip3 install requests

CMD [ "python3", "./pcpe_metrics_collector.py" ]
