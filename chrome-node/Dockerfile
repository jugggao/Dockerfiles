FROM debian:11.2

RUN apt-get update && \
    apt-get clean && \
    apt-get install -y gnupg2 x11vnc xvfb fluxbox wmctrl ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy wget curl && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get -y install google-chrome-stable

RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    apt-get install -y ffmpeg && \
    apt-get clean

RUN useradd apps && \
    mkdir -p /home/apps && \
    chown -v -R apps:apps /home/apps && \
    mkdir -p /data/app

# COPY --chown=apps:apps app/ /home/apps/app 

USER apps

COPY bootstrap.sh /

WORKDIR /home/apps/app
CMD '/bootstrap.sh'