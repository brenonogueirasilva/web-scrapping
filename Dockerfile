FROM python:3.10.6-slim

# Install Google Chrome
RUN apt-get update && apt-get install -y wget unzip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
RUN apt install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb
RUN apt-get clean

ENV LOCAL=False

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./code/ 

WORKDIR /code

CMD ["bash"]

# ENTRYPOINT [ "bin/bash" ]
# CMD ["python", "main.py"]

