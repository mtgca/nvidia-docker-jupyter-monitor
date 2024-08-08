## nvidia-docker-jupyter-monitor

This project is a modification of [AllenCellModeling/nvidia-docker-stats](https://github.com/AllenCellModeling/nvidia-docker-stats.git). We are using this as a base to monitor system resource usage, including GPU processes, and have added the retrieval of Jupyter Notebook tokens associated with Docker containers using the Colab image.

## About

A Python 3 based command line tool for determining a docker container associated processes gpu utilization by joining information across 'nvidia-smi _' and 'docker _' commands.

## New Features

- **Jupyter Notebook Tokens**: Retrieving Jupyter Notebook tokens associated with Docker containers using the Colab image.
- **Docker File for a Notion Monitoring automatization**: Fills a Notion Database with the Docker stats and Jupyter Notebook tokens information
- (Comming Soon..)**Resource Monitoring**: Monitoring system resource usage by Docker containers.

### Dockerfile Usage

- Clone the repository
  ```
  git clone https://github.com/mtgca/nvidia-docker-jupyter-monitor.git
  ```
- Go to the path of the Dockerfile
  ```
  cd nvidia-docker-jupyter-monitor/nvidiadockerstats/NotionDocker/
  ```
- Create a `.env` file with the following information
  ```
  Notion_Token=Insert your Notion integration token
  Database_ID=Insert your Notion database ID
  ```
- Build the Docker image
  ```
  docker build -t NotionDocker .
  ```
- Run the container with access to the host's Docker, and Nvidia information
  ```
  docker run --gpus=all --pid=host -v /var/run/docker.sock:/var/run/docker.sock --name dockerNv NotionDocker
  ```

## Usage of AllenCellModeling version

### Case 1

Clone into the python path and run module as script via:

```
$ python3 -m nvidiadockerstats.nvidiadockerstats
```

### Case 2

Clone anywhere on network home, link, and run directly:

```
$ git clone https://github.com/cdw/nvidia-docker-stats.git
$ ln nvidia-docker-stats/nvidiadockerstats/nvidiadockerstats.py ~/.local/bin/nvidiadockerstats
$ nvidiadockerstats
```

### Example output

```
Container       Image                   pid     gpu_uuid        used_memory     used_gpu
9afcd2624a5b    shiva/keras
					30920   0                11207 MiB       0 %
					30920   1                11587 MiB       0 %
					30920   2                11587 MiB       0 %
					30920   3                11251 MiB       0 %
5eca98f0fa0f    vishnu/pytorch_ext
					8846    0                401 MiB         0 %
					8846    3                353 MiB         0 %
```

## License

This project is licensed under the GNU General Public License, version 3.(GPL 3) See the [LICENSE](./LICENSE) file for details.
This project is based on the work done in [AllenCellModeling/nvidia-docker-stats](https://github.com/AllenCellModeling/nvidia-docker-stats.git).
Thanks to the original authors.
Modifications and maintenance by [mtgca](https://github.com/mtgca), [Pichuelectrico](https://github.com/Pichuelectrico), and [agualat](https://github.com/agualat).
