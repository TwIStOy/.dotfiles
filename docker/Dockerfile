from ubuntu:18.04

RUN sed -i 's/security.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/cn.archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

RUN apt update && apt install -y sudo git wget curl python python3

RUN sed -i 's/ALL$/NOPASSWD:ALL/g' /etc/sudoers

RUN useradd -rm -d /home/hawtian -s /bin/bash -g root -G sudo -u 1000 hawtian

USER hawtian
WORKDIR /home/hawtian

ENV https_proxy=http://127.0.0.1:8899 http_proxy=http://127.0.0.1:8899 all_proxy=socks5://127.0.0.1:8899


