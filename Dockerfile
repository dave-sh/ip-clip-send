# I'm relatively new to containerization technology, but I heard alpine was a lightweight linux distribution that would be good for a microservice

FROM python:3.8.10-slim AS build-stage

RUN apt-get update && apt-get install -y \
    autoconf \
    automake \
    curl \
    gcc \
    git \
    ipset \
    kmod \
    make \
    pkg-config \
    procps \
    traceroute \
    zlib1g-dev \
    bash \
    iproute2 \
    cron \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/* 

WORKDIR /app

RUN git clone https://github.com/firehol/iprange.git iprange.git && \
    git clone https://github.com/firehol/firehol.git firehol.git

WORKDIR /app/iprange.git
RUN chmod +x autogen.sh && \
    ./autogen.sh && \
    ./configure --prefix=/usr CFLAGS="-march=native -O3" --disable-man && \
    make && \
    make install

WORKDIR /app/firehol.git
RUN chmod +x autogen.sh && \
    ./autogen.sh && \
    ./configure --prefix=/usr --sysconfdir=/etc --disable-man --disable-doc && \
    make && \
    make install

RUN mkdir -p /usr/var/run

WORKDIR /app

# enable whichever IP sets you would like to be included in the API here, I just used all the lists from firehol level 1 in mine, but for testing purposes only included one 
# you can find the full list on the firehol website
# https://iplists.firehol.org/

RUN update-ipsets enable dshield

# if you just want a firehol docker file that will grab ips, you can comment out the rest of the Dockerfile 

# second build stage with Python FastAPI program, originally this had one because it was alpine, but I didn't know the environments used debian by default because Im dumb

RUN mkdir -p /ipsec_api

WORKDIR /ipsec_api

RUN pip install -U pip && pip install pipenv

COPY Pipfile Pipfile.lock /ipsec_api/

RUN pipenv install --system --deploy

COPY api.py /ipsec_api/
COPY schemas.py /ipsec_api/
COPY openapi.yaml /ipsec_api/
COPY server.py /ipsec_api/
COPY updateDatabase.py /ipsec_api/

# cron job to update the database by running the update-ipsets and python script daily 
COPY crontab /etc/cron.d/crontab 
RUN chmod 0644 /etc/cron.d/crontab 
RUN touch /var/log/cron.log

# Start cron and uvicorn server
COPY start_service.sh /ipsec_api/
RUN chmod +x start_service.sh

CMD ["./start_service.sh"]
