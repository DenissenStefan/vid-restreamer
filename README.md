# Project Title

This project is intended to restream video streams. It is created out of a use case where multicast videofeeds needed to be converted to unicast streams keeping the FMV KLV data intact.

## Getting Started

These instructions will get you a container up and running in your docker environment.

### Prerequisites

- Docker

### Installing

### Docker run

```sh
docker run --name restream -v /path/to/streams.csv:/etc/restream/streams.csv -p 8554:8554 --restart unless-stopped denissenstefan/restream:latest
```

### Docker-Compose

Location of the CSV with the videostreams is located at `/etc/restream/streams.csv` in the container.

```yml
version: '3.7'
services:
  restream:
    image: denissenstefan/restream:latest
    container_name: restream
    volumes:
      - /path/to/streams.csv:/etc/restream/streams.csv
    ports:
      - "8554:8554"
    restart: unless-stopped
```

### streams.csv

```
input,alias
rtmp://localhost:1935/live/stream1,stream1
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](http://website.com) file for details
