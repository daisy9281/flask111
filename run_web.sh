#!/bin/bash

# 安装必要的依赖，使用国内镜像源并增加超时时间
pip3 install --timeout 120 --index-url https://pypi.tuna.tsinghua.edu.cn/simple flask requests beautifulsoup4

# 运行Flask应用，使用不同的端口
python3 app.py --port 5001