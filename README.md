# Video Restreamer

This project is intended to restream STANAG 4609 or Full Motion Video (FMV) streams. It is created out of a use case where multicast videofeeds needed to be converted to unicast streams keeping the FMV KLV data intact.

Currently the following restream options are supported by the container:

| Input | Output | Status |
| --- | --- | --- |
| Multicast | Multicast | :white_check_mark: Working |
| SRT | Multicast | :question: Not yet tested |
| Multicast | SRT | :question: Not yet tested |

## Getting Started

These instructions will get you a container up and running in your docker environment. After the container has started one can browse to `http://<ip address>:5000` for the GUI to add and remove video streams.

### Prerequisites

- Docker

### Installing

If doing a GIT clone it is possible to execute a `docker compose build` followed by `docker compose up -d` command to build & start the container.

### Docker run

```sh
docker run --net host --name denissenstefan/restream:latest -v ./config.yaml:/app/config.yaml --restart unless-stopped 
```

### Docker-Compose

```yml
version: '3.8'

services:
  restreamer:
    network_mode: host
    container_name: denissenstefan/restream:latest
    volumes:
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
```

### config.yaml

```yaml
streams:
- input: udp://236.1.2.3:18000
  name: multicast-to-multicast-example
  output: udp://236.1.2.4:18000
- input: srt://
  name: unicast-to-multicast-example
  output: udp://236.1.2.4:18000
- input: udp://236.1.2.3:18000
  name: multicast-to-unicast-example
  output: srt://
```

## Known issues
The original project and the 2.0.0 version have been quickly put together, there might be bugs or unwanted behaviour. THe following issues are known:

- Health status shows "unhealthy" even though the streams are working

## Contributing

You can contribute by either raising issues or do a pull request for your additional code.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
