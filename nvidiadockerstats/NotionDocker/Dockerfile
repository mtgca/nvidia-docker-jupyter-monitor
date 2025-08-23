FROM python:latest

# Set the working directory
WORKDIR /code

# Copy the requirements file and install the dependencies
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Install Docker CLI inside the container
RUN apt-get update && apt-get install -y docker.io 

# Copy the Python scripts, shell script, and environment files into the container
COPY ./jupytertoken_extraction.py /code/
COPY ./NotionAutoUpdateBot.py /code/
COPY ./auto.py /code/
COPY ./model.py /code/
COPY ./*.env /code/

# Set the default command to run the shell script
CMD ["python3", "/code/auto.py"]