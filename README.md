## nvidia-docker-jupyter-monitor

This project is a modification of [AllenCellModeling/nvidia-docker-stats](https://github.com/AllenCellModeling/nvidia-docker-stats.git). We are using this as a base to monitor system resource usage, including GPU processes, and have added the retrieval of Jupyter Notebook tokens associated with Docker containers using the Colab image.

## About

A Python 3 based command line tool for determining a docker container associated processes gpu utilization by joining information across 'nvidia-smi _' and 'docker _' commands.

## New Features

- **Jupyter Notebook Tokens**: Retrieving Jupyter Notebook tokens associated with Docker containers using the Colab image.
- (Comming Soon..)**Resource Monitoring**: Monitoring system resource usage by Docker containers.

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

GPL 3
