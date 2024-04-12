FROM ubuntu:jammy
RUN echo "Acquire::http::proxy \"$HTTP_PROXY\";\nAcquire::https::proxy \"$HTTPS_PROXY\";" > /etc/apt/apt.conf.d/proxy.conf
RUN cat /etc/apt/apt.conf.d/proxy.conf
RUN apt update
RUN apt install lsb-release curl gpg -y
RUN curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list
RUN apt update && apt install -y \
    redis \
    python3-pip  \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ADD app.py ./
ADD vgmdl.py ./
ADD requirements.txt ./
ADD templates ./templates
ADD routes ./routes
ADD models ./models
ADD static ./static
# RUN git clone https://github.com/geo-petrini/vgm_dl /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD redis-server --daemonize yes && python3 app.py
