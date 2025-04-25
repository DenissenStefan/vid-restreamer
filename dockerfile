FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    python3 \
    python3-pip \
    supervisor \
    curl

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app
COPY supervisord.conf /etc/supervisord.conf
WORKDIR /app

RUN mkdir -p /etc/supervisor/conf.d /var/log
RUN chmod +x /app/start.sh

EXPOSE 5000 8000
CMD ["/app/start.sh"]