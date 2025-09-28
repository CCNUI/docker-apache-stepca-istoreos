# /mnt/data/apache_web_server/apache/Dockerfile
# 用于构建包含Python3(mod_wsgi)和WebDAV支持的Apache镜像 (修正版)

# 基于官方的 Apache 镜像
FROM httpd:latest

# 安装 Python3, mod_wsgi, 和 apache2-utils (用于 htpasswd)
# 注意：官方 httpd 镜像是基于 Debian 的，所以使用 apt-get
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    libapache2-mod-wsgi-py3 \
    apache2-utils \
    && rm -rf /var/lib/apt/lists/*

# 创建用于 WebDAV 锁数据库的目录
RUN mkdir -p /var/lib/dav
