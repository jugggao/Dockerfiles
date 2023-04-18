FROM ubuntu:jammy

LABEL author="jugg.gao@qq.com"

# Install JDK8
RUN apt-get update -y && \
    apt-get install -y python3

# Install ffmpeg
RUN apt-get install -y ffmpeg

# Timezone settings.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
RUN apt-get -y install tzdata

# Clean
RUN apt-get remove --purge --auto-remove -y

CMD ["/bin/bash"]