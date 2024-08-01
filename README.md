## About

Using the AllenCellModeling/nvidia-docker-stats repository as a base
a program that obtains the Jupyter Notebook token associated with the Docker containers that use the Colab image and in turn allows to determine the GPU utilization of the processes associated with the Docker containers by joining the information through the commands 'nvidia-smi _' and 'docker _'.

## Usage

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
