FROM python:3.12-slim 

COPY requirements.txt /

RUN pip install -r /requirements.txt

WORKDIR /app

COPY *.py .

CMD ["python","main.py"]