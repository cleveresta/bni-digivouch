FROM python:3.7-slim
ADD app /run
WORKDIR /run
COPY app/requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "sqs_reader.py"]