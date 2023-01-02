# --------------------
# Building stage image
# --------------------
FROM debian:11.5 AS builder

ARG NGINX_VERSION=1.22.0
ARG NGINX_VOD_MODULE_VERSION=1.29
ARG NGINX_SECURE_TOKEN_MODULE_VERSION=1.4
ARG NGINX_AKAMAI_TOKEN_VALIDATE_MODULE_VERSION=1.1
ARG NGINX_RTMP_MODULE_VERSION=1.21.0
ARG NGINX_MODULE_VTS_VERSION=0.1.18
ARG FFMPEG_VERSION=5.1

RUN apt-get update -y && \
    apt-get install -y curl tar gzip && \
    # build environment
    apt-get install -y build-essential yasm && \
    # Pcre jit
    apt-get install -y libpcre3 libpcre3-dev && \
    # Font library
    apt-get install -y libfreetype6-dev && \
    # Nginx HTTP gzip static
    apt-get install -y zlib1g-dev && \
    # Nginx HTTP ssl module
    apt-get install -y openssl libssl-dev && \
    # Nginx HTTP image filter
    apt-get install -y libgd-dev && \
    # Nginx GeoIp module
    apt-get install -y libgeoip-dev && \
    # Nginx HTTP xslt module
    apt-get install -y libxslt-dev && \
    # Nginx VOD module
    apt-get install -y libavcodec-dev libswscale-dev libavfilter-dev && \
    # FFMPEG --enable-libmp3lame
    apt-get install -y libmp3lame-dev && \
    # FFMPEG --enable-libvpx
    apt-get install -y libvpx-dev && \
    # FFMPEG --enable-librtmp
    apt-get install -y librtmp-dev && \
    # FFMPEG --enable-libtheora
    apt-get install -y libtheora-dev && \
    # FFMPEG --enable-libvorbis
    apt-get install -y libvorbis-dev && \
    # FFMPEG --enable-libvpx
    apt-get install -y libvpx-dev && \
    # FFMPEG --enable-libx264 ps. libx264 requies --enable-gpl
    apt-get install -y libx264-dev && \
    # FFMPEG --enable-libx265 ps. It's needed to add --extra-libs="-lpthread"
    # Reference: ​https://bitbucket.org/multicoreware/x265_git/issues/371/x265-not-found-using-pkg-config
    apt-get install -y libx265-dev libnuma-dev

RUN mkdir -p /tmp/build

WORKDIR /tmp/build

RUN mkdir -p nginx nginx-vod-module nginx-secure-token-module nginx-akamai-token-validate-module nginx-rtmp-module nginx-module-vts ffmpeg
RUN curl -sL https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz | tar -zx -C nginx --strip 1
RUN curl -sL https://github.com/kaltura/nginx-vod-module/archive/refs/tags/${NGINX_VOD_MODULE_VERSION}.tar.gz | tar -zx -C nginx-vod-module --strip 1
RUN curl -sL https://github.com/kaltura/nginx-secure-token-module/archive/refs/tags/${NGINX_SECURE_TOKEN_MODULE_VERSION}.tar.gz | tar -zx -C nginx-secure-token-module --strip 1
RUN curl -sL https://github.com/kaltura/nginx-akamai-token-validate-module/archive/refs/tags/${NGINX_AKAMAI_TOKEN_VALIDATE_MODULE_VERSION}.tar.gz | tar -zx -C nginx-akamai-token-validate-module --strip 1
RUN curl -sL https://github.com/kaltura/nginx-rtmp-module/archive/refs/tags/v${NGINX_RTMP_MODULE_VERSION}.tar.gz | tar -zx -C nginx-rtmp-module --strip 1
RUN curl -sL https://github.com/vozlt/nginx-module-vts/archive/refs/tags/v${NGINX_MODULE_VTS_VERSION}.tar.gz | tar -zx -C nginx-module-vts --strip 1
RUN curl -sL https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.gz | tar -zx -C ffmpeg --strip 1

WORKDIR /tmp/build/nginx

RUN ./configure \
    --sbin-path=/usr/local/sbin/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --http-log-path=/var/log/nginx/access.log \
    --error-log-path=/var/log/nginx/error.log \
    --pid-path=/var/run/nginx/nginx.pid \
    --lock-path=/var/lock/nginx.lock \
    --modules-path=/usr/lib/nginx/modules \
    --http-client-body-temp-path=/var/lib/nginx/body \
    --http-fastcgi-temp-path=/var/lib/nginx/fastcgi \
    --http-proxy-temp-path=/var/lib/nginx/proxy \
    --http-scgi-temp-path=/var/lib/nginx/scgi \
    --http-uwsgi-temp-path=/var/lib/nginx/uwsgi \
    --with-compat \
    --with-debug \
    --with-pcre-jit \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_v2_module \
    --with-http_slice_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_auth_request_module \
    --with-http_image_filter_module \
    --with-http_xslt_module \
    --with-stream \
    --with-stream_ssl_module \
    --with-stream_geoip_module \
    --with-stream_realip_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-file-aio \
    --with-threads \
    --with-cc-opt="-O3" \
    --add-module=../nginx-vod-module \
    --add-module=../nginx-secure-token-module \
    --add-module=../nginx-akamai-token-validate-module \
    --add-module=../nginx-rtmp-module \
    --add-module=../nginx-module-vts && \
    make -j $(getconf _NPROCESSORS_ONLN) && \
    make install

WORKDIR /tmp/build/ffmpeg

RUN  ./configure \
    --enable-version3 \
    --enable-gpl \
    --enable-small \
    --enable-libx264 \
    --enable-libx265 \
    --enable-libvpx \
    --enable-libtheora \
    --enable-libvorbis \
    --enable-librtmp \
    --enable-postproc \
    --enable-swresample \ 
    --enable-libfreetype \
    --enable-libmp3lame \
    --disable-debug \
    --disable-doc \
    --disable-ffplay \
    --extra-libs="-lpthread -lm" && \
    make -j $(getconf _NPROCESSORS_ONLN) && \
    make install

RUN cp /tmp/build/nginx-rtmp-module/stat.xsl /usr/local/nginx/html/stat.xsl

# ------------------------
# Building the final image
# ------------------------
FROM debian:11.5-slim

RUN apt-get update -y && \
    # PERL
    apt-get install -y libpcre3 libpcre3-dev && \
    # HTTP gzip static
    apt-get install -y zlib1g-dev && \
    # HTTP ssl module
    apt-get install -y openssl libssl-dev && \
    # HTTP image filter
    apt-get install -y libgd-dev && \
    # GeoIp
    apt-get install -y libgeoip-dev && \
    # HTTP xslt module
    apt-get install -y libxslt-dev && \
    # VOD module
    apt-get install -y libavcodec-dev libswscale-dev libavfilter-dev && \
    # libmp3lame
    apt-get install -y libmp3lame0 && \
    # FFMPEG --enable-libvpx
    apt-get install -y libvpx-dev && \
    # librtmp
    apt-get install -y librtmp1 && \
    # libtheora
    apt-get install -y libtheora0 && \
    # libvorbis
    apt-get install -y libvorbis-dev && \
    # libvpx
    apt-get install -y libvpx6 && \
    # libx264
    apt-get install -y libx264-dev && \
    # libx265
    apt-get install -y libx265-dev libnuma-dev && \
    # htop tool
    apt-get install -y htop && \
    # Clean
    apt-get remove --purge --auto-remove -y

COPY --from=builder /usr/local /usr/local
COPY --from=builder /etc/nginx /etc/nginx
COPY --from=builder /var/log/nginx /var/log/nginx
COPY --from=builder /var/lock /var/lock
COPY --from=builder /var/run/nginx /var/run/nginx
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY players/hls_basic.html /usr/local/nginx/html/index.html

RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    mkdir -p /var/lib/nginx/{body,fastcgi,proxy,scgi,uwsgi} && \
    mkdir -p /data

EXPOSE 1935
EXPOSE 80
VOLUME /data

ENTRYPOINT ["/usr/local/sbin/nginx"]
CMD ["-g", "daemon off;"]
