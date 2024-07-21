FROM python:slim
ARG OWM_KEY
ARG WAQI_KEY
ENV OWM_KEY=$OWM_KEY
ENV WAQI_KEY=$WAQI_KEY
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . /app
WORKDIR /app
RUN chmod +x deploy.sh
ENTRYPOINT ["./deploy.sh"]