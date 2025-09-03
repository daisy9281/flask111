from flask import Flask, render_template, request, jsonify
import os
import sys
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 导入原有的函数
def get_zego_packages(word):
    url = f"https://pub.dev/packages?q={word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: pubdev failed: {e}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    # 1. find div class="packages"
    packages = soup.find('div', class_='packages')
    if not packages:
        return []
    # 2. loop divs
    results = ["name", "version", "update_time"]
    data = []
    for package in packages.find_all('div', class_='packages-item'):
        res = []
        # get packages-header text
        header = package.find('div', class_='packages-header')
        if not header:
            continue
        #find h3/a in header
        h3 = header.find('h3')
        if not h3:
            continue
        a = h3.find('a')
        if not a:
            continue
        res.append(a.text)
        # find span packages-metadata-block
        metadata = package.find('span', class_='packages-metadata-block')
        if not metadata:
            continue
        # find multi a
        a = metadata.find_all('a')
        if len(a) < 2:
            continue
        res.append(a[0].text)
        res.append(a[1].text)
        data.append(res)
    return data

def get_npmjs_packages(word):
    # get https://www.npmjs.com/search?q=zego resp
    url = f"https://www.npmjs.com/search?q={word}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: npmjs failed: {e}")
        return []
    # soup
    soup = BeautifulSoup(response.text, 'html.parser')
    # 1.find all section
    sections = soup.find_all('section')
    # loop sections
    data = []
    for section in sections:
        res = []
        # 1.find a target="_self"
        a = section.find('a', target="_self")
        if a is None:
            continue
        #find h3
        h3 = a.find('h3')
        if not h3:
            continue
        res.append(h3.text)
        # 2.find span class iclass="_66c2abad flex-grow-1"
        span = section.find('span', class_="_66c2abad flex-grow-1")
        if not span:
            continue
        # span.text 删除非ascii字符
        span_text = span.text.encode('ascii', 'ignore').decode('ascii').split()
        if not span_text:
            continue
        version = span_text[0]
        others = " ".join(span_text[1:4]) if len(span_text) > 1 else ""
        res.append(version)
        res.append(others)
        data.append(res)
    return data

@app.route('/')
def index():
    return render_template('index.html', keyword='')

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form.get('keyword', 'zego')
    exact_match = request.form.get('exact_match') == 'on'  # 获取精准查询状态
    
    # 分割逗号分隔的包名
    keywords = [kw.strip() for kw in keyword.split(',') if kw.strip()]
    
    # 初始化结果列表
    pubdev_data = []
    npmjs_data = []
    
    # 对每个包名进行查询
    for kw in keywords:
        # 获取数据
        pub_results = get_zego_packages(kw)
        npm_results = get_npmjs_packages(kw)
        
        # 根据精准查询状态决定是否只取第一个结果
        if pub_results:
            if exact_match:
                pubdev_data.append(pub_results[0])  # 只添加第一个结果
            else:
                pubdev_data.extend(pub_results)  # 添加所有结果
        if npm_results:
            if exact_match:
                npmjs_data.append(npm_results[0])  # 只添加第一个结果
            else:
                npmjs_data.extend(npm_results)  # 添加所有结果
    
    return render_template('index.html', 
                          keyword=keyword,
                          pubdev_data=pubdev_data,
                          npmjs_data=npmjs_data)

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
        # 创建index.html文件
        with open('templates/index.html', 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>包搜索工具</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        form { margin-bottom: 20px; }
        input { padding: 8px; width: 300px; }
        button { padding: 8px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
        .results { margin-top: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
        .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; color: black; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #ccc; }
        .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
    </style>
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        // 默认显示第一个标签
        document.addEventListener("DOMContentLoaded", function() {
            document.getElementsByClassName("tablinks")[0].click();
        });
    </script>
</head>
<body>
    <h1>包搜索工具</h1>
    <form action="/search" method="post">
        <input type="text" name="keyword" placeholder="请输入搜索关键词" value="{{ keyword }}" required>
        <button type="submit">搜索</button>
    </form>
    
    <div class="results">
        <div class="tab">
            <button class="tablinks" onclick="openTab(event, 'pubdev')">Pub.dev 结果</button>
            <button class="tablinks" onclick="openTab(event, 'npmjs')">NPM.js 结果</button>
        </div>
        
        <div id="pubdev" class="tabcontent">
            <h2>Pub.dev 搜索结果 (关键词: {{ keyword }})</h2>
            {% if pubdev_data %}
            <table>
                <tr>
                    <th>包名</th>
                    <th>版本</th>
                    <th>更新时间</th>
                </tr>
                {% for item in pubdev_data %}
                <tr>
                    <td>{{ item[0] }}</td>
                    <td>{{ item[1] }}</td>
                    <td>{{ item[2] }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>没有找到相关的包信息</p>
            {% endif %}
        </div>
        
        <div id="npmjs" class="tabcontent">
            <h2>NPM.js 搜索结果 (关键词: {{ keyword }})</h2>
            {% if npmjs_data %}
            <table>
                <tr>
                    <th>包名</th>
                    <th>版本</th>
                    <th>其他信息</th>
                </tr>
                {% for item in npmjs_data %}
                <tr>
                    <td>{{ item[0] }}</td>
                    <td>{{ item[1] }}</td>
                    <td>{{ item[2] }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>没有找到相关的包信息</p>
            {% endif %}
        </div>
    </div>
</body>
</html>''')
    # 解析命令行参数获取端口
    import sys
    port = 5000  # 默认端口
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        try:
            port = int(sys.argv[2])
        except ValueError:
            print('Invalid port number, using default 5000')
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=port)