FROM ubuntu
RUN apt-get update && apt-get install -y ffmpeg
COPY ./restream.sh /usr/local/bin/restream.sh
RUN chmod +x /usr/local/bin/restream.sh
EXPOSE 8554
ENTRYPOINT [ "/usr/local/bin/restream.sh" ]