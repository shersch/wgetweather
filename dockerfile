FROM python:slim
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . /app
WORKDIR /app
RUN chmod +x deploy.sh
ENTRYPOINT ["./deploy.sh"]