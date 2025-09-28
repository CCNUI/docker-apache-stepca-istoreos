```markdown
# Docker Apache + Python + WebDAV + Step-CA on iStoreOS/OpenWRT

一套完整的 Docker Compose 方案，用于在 iStoreOS/OpenWRT 等嵌入式Linux系统上快速部署一个安全、强大的 Apache, Python, WebDAV 及私有CA (Step-CA) 服务器。

该项目是解决一系列真实部署挑战后的最终成果，特别适合希望在软路由、NAS等设备上搭建功能全面的个人或团队 Web 服务的用户。

## ✨ 特性

- **Apache Web 服务器**: 搭载 Python CGI 和 WebDAV 模块。
- **Python 3 支持**: 可直接运行 `.py` 脚本。
- **WebDAV**: 提供基于密码认证的网络文件存储。
- **Step-CA**: 内置一个强大的私有证书颁发机构，用于签发内网服务的 SSL/TLS 证书。
- **高度可配置**: 所有端口、域名、路径均可通过配置文件修改。
- **兼容性强**: 基于 `python` 镜像构建，保证了各组件的无缝兼容。

## 📁 目录结构

```

.
├── apache/
│   ├── cgi-bin/
│   │   └── test.py
│   ├── conf/
│   │   └── 000-default.conf
│   ├── htdocs/
│   │   └── index.html
│   ├── logs/
│   ├── webdav/
│   │   └── .htpasswd
│   └── Dockerfile
├── docker-compose.yml
└── step-ca/
├── certs/
├── config/
├── db/
└── secrets/

````

## 🚀 部署指南

1.  **准备环境**: 克隆本仓库或手动创建以上目录结构。
2.  **创建配置文件**: 将下方的文件内容填充到对应位置。
3.  **初始化CA**: 这是一个关键的手动过程，因为自动初始化在某些环境下不可靠。
    * 临时修改 `docker-compose.yml`，在 `ca` 服务下添加 `command: sleep infinity`。
    * 运行 `docker-compose up -d ca`。
    * 运行 `docker-compose exec ca step ca init` 并根据提示完成交互式设置。
    * 通过 `docker-compose exec ca id` 获取用户ID，并在主机上运行 `chown -R [UID]:[GID] ./step-ca` 修复权限。
    * 将CA密码存入 `./step-ca/secrets/password` 文件。
    * 移除 `command: sleep infinity` 并根据最终版 `docker-compose.yml` 添加 `extra_hosts` 和 `STEP_CA_PASSWORD_FILE`。
4.  **签发服务器证书**:
    ```bash
    docker-compose up -d --force-recreate ca
    # 根据你的域名修改
    docker-compose exec ca step ca certificate your.domain.com ...
    ```
5.  **创建WebDAV用户**:
    ```bash
    docker-compose run --rm --entrypoint htpasswd apache -bc /var/www/htpasswd/.htpasswd your_user your_password
    ```
6.  **构建并启动**:
    ```bash
    docker-compose build --no-cache apache
    docker-compose up -d
    ```
7.  **验证**:
    * 在客户端设备上安装 `./step-ca/certs/root_ca.crt` 根证书。
    * 访问 `https://your.domain.com:444` (请使用你在配置中设置的端口)。

---
### 配置文件内容

#### `docker-compose.yml`
```yaml
# version: '3.8' ... (此处粘贴最终版的 docker-compose.yml 内容)
version: '3.8'

services:
  apache:
    build:
      context: ./apache
    container_name: apache_web_server
    restart: unless-stopped
    ports:
      - "81:80"
      - "444:443"
    volumes:
      - ./apache/conf/000-default.conf:/etc/apache2/sites-available/000-default.conf
      - ./apache/htdocs:/var/www/html
      - ./apache/cgi-bin:/usr/lib/cgi-bin
      - ./apache/logs:/var/log/apache2
      - ./apache/webdav:/var/www/webdav
      - ./apache/webdav/.htpasswd:/var/www/htpasswd/.htpasswd
      - ./step-ca/certs/apache/server.crt:/etc/ssl/certs/apache/server.crt
      - ./step-ca/certs/apache/server.key:/etc/ssl/private/apache/server.key
    depends_on:
      - ca
    networks:
      - web_net

  ca:
    image: smallstep/step-ca:latest
    container_name: certificate_authority
    restart: unless-stopped
    volumes:
      - ./step-ca:/home/step
    environment:
      STEPPATH: /home/step
      STEP_CA_PASSWORD_FILE: /home/step/secrets/password
    extra_hosts:
      - "ca.your.domain.com:127.0.0.1" # 请替换为你的CA域名
    networks:
      - web_net

networks:
  web_net:
    driver: bridge
````

#### `apache/Dockerfile`

```dockerfile
# FROM python:3.9-slim-bullseye ... (此处粘贴最终版的 Dockerfile 内容)
FROM python:3.9-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    apache2-utils \
    nano \
    && rm -rf /var/lib/apt/lists/*

RUN a2enmod ssl wsgi dav dav_fs rewrite headers

RUN chown -R www-data:www-data /var/www/html
RUN chown -R www-data:www-data /var/log/apache2

CMD ["apache2ctl", "-D", "FOREGROUND"]
```

#### `apache/conf/000-default.conf`

```apache
# <VirtualHost *:80> ... (此处粘贴最终版的 Apache 配置文件内容)
<VirtualHost *:80>
    ServerName your.domain.com # 请替换为你的域名
    Redirect permanent / [https://your.domain.com:444/](https://your.domain.com:444/) # 请替换为你的域名和端口
</VirtualHost>

<VirtualHost *:443>
    ServerName your.domain.com # 请替换为你的域名
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile    /etc/ssl/certs/apache/server.crt
    SSLCertificateKeyFile /etc/ssl/private/apache/server.key

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin/">
        AllowOverride None
        Options +ExecCGI
        Require all granted
        AddHandler cgi-script .py
    </Directory>

    Alias /webdav /var/www/webdav
    <Directory /var/www/webdav>
        DAV On
        AuthType Basic
        AuthName "WebDAV"
        AuthUserFile /var/www/htpasswd/.htpasswd
        Require valid-user
    </Directory>
</VirtualHost>
```

```

#### **.gitignore:**

```

# Log files

apache/logs/\*.log

# Step-CA data, certificates, and secrets - DO NOT COMMIT TO GIT

step-ca/

# WebDAV password file

apache/webdav/.htpasswd

# OS-specific files

.DS\_Store
Thumbs.db

# IDE/Editor files

.vscode/
.idea/
\*.swp
\*\~

```
```
