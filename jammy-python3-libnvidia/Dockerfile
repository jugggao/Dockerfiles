FROM busybox:1.36 AS builder

RUN wget --no-check-certificate -qP /tmp https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/libnvidia-compute-470_470.161.03-0ubuntu1_amd64.deb && \
    wget --no-check-certificate -qP /tmp https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/libnvidia-decode-470_470.161.03-0ubuntu1_amd64.deb && \
    wget --no-check-certificate -qP /tmp https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/libnvidia-encode-470_470.161.03-0ubuntu1_amd64.deb

FROM ubuntu:22.04

LABEL maintainer="jugg.gao@gmail.com"
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install python and pip
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt-get update -y && \
    apt-get install -y python3 python3-pip

# Install ffmpeg
RUN apt-get update -y && \
    apt-get install -y ffmpeg && \
    apt-get remove --purge --auto-remove -y


# Install libnvidia

COPY --from=builder /tmp/libnvidia*.deb /tmp/

RUN apt-get update -y && \
    apt-get install -y libbsd0 libmd0 libx11-6 libx11-data libxau6 libxcb1 libxdmcp6 libxext6 && \
    dpkg -i /tmp/libnvidia*.deb  && \
    apt-get remove --purge --auto-remove -y && \
    rm -f /tmp/libnvidia.*.deb

# Timezone settings.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
RUN apt-get -y install tzdata