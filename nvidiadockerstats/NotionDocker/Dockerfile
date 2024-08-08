# 
FROM python:latest

# 
WORKDIR /code

#
COPY ~/NVIDIA-DOCKER-JUPYTER-MONITOR/requirements /code/

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt-get update && apt-get install -y docker.io 

#
COPY ./jupytertoke_extraction.py /code/
COPY ./NotionAutoUpdateBot.py /code/
COPY ./main.sh /code/
COPY ./*.env /code/

# 
CMD ["bash", "main.sh"]