## nvidia-docker-jupyter-monitor

This project is a modification of [AllenCellModeling/nvidia-docker-stats](https://github.com/AllenCellModeling/nvidia-docker-stats.git). We are using this as a base to monitor system resource usage, including GPU processes, and have added the retrieval of Jupyter Notebook tokens associated with Docker containers using the Colab image.

## About

A Python 3 based command line tool for determining a docker container associated processes gpu utilization by joining information across 'nvidia-smi _' and 'docker _' commands.

## New Features

- **Jupyter Notebook Tokens**: Retrieving Jupyter Notebook tokens associated with Docker containers using the Colab image.
- **Dockerfile for a Notion monitoring automation** - Populate a Notion database with Docker statistics and Jupyter Notebook token information
- (On Progress..)**Per-container resource monitoring**: Monitoring system resource usage by Docker containers, such as container GPU usage, this was done by modifying the [nawafalageel/docker_container_gpu_exporter](https://github.com/nawafalageel/docker_container_gpu_exporter.git) repository,
  which was a Docker Container GPU Exporter for Prometheus, from which the `p2g.sh` file and some of the program logic was used.

### Dockerfile Usage

> [!IMPORTANT]
>
> - First, in Notion, prepare the database by following the format below for the properties: (Name | Type)
>   - Container ID | Text
>   - Docker container | Title
>   - Jupyter Token | Formula (Formula:`"http://127.0.0.1:"+prop("Port Number")+"/?token="+prop("Token")`)
>   - Port Number | Number (Number format: Number)
>   - Token | Text
>   - CPU Usage | Number (Number format: Percent)
>   - Memory Usage | Text
>   - Memory Usage Percent | Number (Number format: Percent)
>   - Network I/O | Text
>   - Block I/O | Text
>   - GPU Usage | Number
>   - GPU Percent | Number
> - Now, in the database, add the Docker Container IDs of the Docker containers that you want to monitor in this database

- Then, clone the repository
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
  docker build -t notiondocker .
  ```
- Run the container with access to the host's Docker, and Nvidia information
  ```
  docker run --gpus=all --pid=host --restart=always -d -v /var/run/docker.sock:/var/run/docker.sock --name dockerNv notiondocker
  ```

### Command Version

- Install the package using pip:
  ```
  pip install -i https://test.pypi.org/simple/ dockergpustats
  ```
- Run the command:
  ```
  dockergpustats
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
