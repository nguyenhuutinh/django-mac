FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user
WORKDIR /home/user/app/backend

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y tesseract-ocr python3-pip

RUN apt-get update \
  && apt-get -y install ffmpeg libsm6 libxext6 # required for opencv

RUN pip3 install pytesseract opencv-python cloudmersive_image_api_client

RUN apt-get install -y libgl1-mesa-glx

# Install system dependencies
RUN apt-get update && apt-get install gcc build-essential libpq-dev -y && \
    python3 -m pip install --no-cache-dir pip-tools

# install python dependencies
ADD *requirements.in /home/user/app/backend/
RUN pip-compile requirements.in > requirements.txt && \
    pip-compile dev-requirements.in > dev-requirements.txt

RUN pip install -r requirements.txt && \
    pip install -r dev-requirements.txt  && \
    pip install psycopg2-binary
# Clean the house
RUN apt-get purge libpq-dev -y && apt-get autoremove -y && \
    rm /var/lib/apt/lists/* rm -rf /var/cache/apt/*

ADD backend/ /home/user/app/backend
# RUN mkdir /home/user/app/data
RUN chown user:user /home/user/app/backend
USER user
CMD gunicorn --timeout 600 telegrambot.wsgi --log-file - -b 0.0.0.0:8000 --reload
