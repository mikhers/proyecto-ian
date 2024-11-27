FROM python:3.10.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    g++ \
    make \
    libboost-python-dev \
    libboost-system-dev \
    libopenblas-dev \
    liblapack-dev \
    && apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

