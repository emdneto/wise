FROM python:3-alpine

WORKDIR /focus
ADD . /focus

RUN pip install -r requirements.txt

CMD ["python3", "core/focus.py"]
