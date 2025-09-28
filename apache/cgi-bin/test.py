#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# /mnt/data/apache_web_server/apache/cgi-bin/test.py
# 这是一个用于测试 Python CGI 是否正常工作的脚本

import sys
import os

# 输出 HTTP 头部
print("Content-Type: text/html;charset=utf-8")
print()

# 输出 HTML 内容
print("<html>")
print("<head><title>Python CGI Test</title></head>")
print("<body>")
print("<h2>Python CGI Script is working!</h2>")
print(f"<p>Python Version: {sys.version}</p>")
print("<h3>Environment Variables:</h3>")
print("<ul>")
for key, value in os.environ.items():
    print(f"<li><b>{key}:</b> {value}</li>")
print("</ul>")
print("</body>")
print("</html>")
