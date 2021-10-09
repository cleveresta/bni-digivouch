FROM jtl-tkgiharbor.hq.bni.co.id/soadev/python:3.6.8-oracle

WORKDIR /app

COPY ./app/ ./
RUN pip3 install --no-cache-dir -r requirements.txt

ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8
EXPOSE 8000

CMD ["uvicorn", "--host=0.0.0.0",  "dbwriter:app"]