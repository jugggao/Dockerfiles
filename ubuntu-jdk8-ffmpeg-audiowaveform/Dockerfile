FROM ubuntu:22.04

LABEL author="jugg.gao@qq.com"

# Install JDK8
RUN apt-get update -y && \
    apt-get install -y openjdk-8-jdk

# Install ffmpeg
RUN apt-get install -y ffmpeg

# Install libnvidia
RUN apt-get update -y && \
    apt-get install -y libnvidia-compute-525 libnvidia-decode-525 libnvidia-encode-525

# Install audiowaveform
RUN apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:chris-needham/ppa && \
    apt-get update -y && \
    apt-get install -y audiowaveform

# Timezone settings.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
RUN apt-get -y install tzdata

# Clean
RUN apt-get remove --purge --auto-remove -y

CMD ["/bin/bash"]