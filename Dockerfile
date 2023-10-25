FROM python:3.9

WORKDIR /app

# https://stackoverflow.com/questions/59812009/what-is-the-use-of-pythonunbuffered-in-docker-file
ENV PYTHONUNBUFFERED True

COPY ./app .
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

# During Docker run you can override the CMD
CMD ["python", "/app/main.py"]
