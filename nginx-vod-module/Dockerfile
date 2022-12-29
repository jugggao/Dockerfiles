FROM debian:11.5 AS builder

RUN apt-get update -y && \
    apt-get install -y curl tar gzip && \
    # gcc
    apt-get install -y build-essential && \
    # pcre jit
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
    apt-get install -y libavcodec-dev libswscale-dev libavfilter-dev

ARG NGINX_VERSION=1.22.0
ARG NGINX_VOD_MODULE_VERSION=1.29
ARG NGINX_SECURE_TOKEN_MODULE_VERSION=1.4
ARG NGINX_AKAMAI_TOKEN_VALIDATE_MODULE_VERSION=1.1
ARG NGINX_RTMP_MODULE_VERSION=1.21.0
ARG NGINX_MODULE_VTS_VERSION=0.1.18

RUN mkdir -p nginx nginx-vod-module nginx-secure-token-module nginx-akamai-token-validate-module nginx-rtmp-module nginx-module-vts
RUN curl -sL https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz | tar -zx -C /nginx --strip 1
RUN curl -sL https://github.com/kaltura/nginx-vod-module/archive/refs/tags/${NGINX_VOD_MODULE_VERSION}.tar.gz | tar -zx -C /nginx-vod-module --strip 1
RUN curl -sL https://github.com/kaltura/nginx-secure-token-module/archive/refs/tags/${NGINX_SECURE_TOKEN_MODULE_VERSION}.tar.gz | tar -zx -C /nginx-secure-token-module --strip 1
RUN curl -sL https://github.com/kaltura/nginx-akamai-token-validate-module/archive/refs/tags/${NGINX_AKAMAI_TOKEN_VALIDATE_MODULE_VERSION}.tar.gz | tar -zx -C /nginx-akamai-token-validate-module --strip 1
RUN curl -sL https://github.com/kaltura/nginx-rtmp-module/archive/refs/tags/v${NGINX_RTMP_MODULE_VERSION}.tar.gz | tar -zx -C /nginx-rtmp-module --strip 1
RUN curl -sL https://github.com/vozlt/nginx-module-vts/archive/refs/tags/v${NGINX_MODULE_VTS_VERSION}.tar.gz | tar -zx -C /nginx-module-vts --strip 1

WORKDIR /nginx

RUN ./configure --prefix=/usr/local/nginx \
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
    make && \
    make install

RUN rm -rf /usr/local/nginx/conf/*.default

FROM debian:11.5-slim

RUN apt-get update -y && \
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
    # ffmpeg
    apt-get install -y ffmpeg && \
    apt-get remove --purge --auto-remove -y

COPY --from=builder /usr/local/nginx /usr/local/nginx

RUN ln -sf /dev/stdout /usr/local/nginx/logs/access.log && \
    ln -sf /dev/stderr /usr/local/nginx/logs/error.log && \
    mkdir -p /data/hls && \
    mkdir -p /data/dash && \
    mkdir -p /data/rec

ENTRYPOINT ["/usr/local/nginx/sbin/nginx"]
CMD ["-g", "daemon off;"]
