import requests
from bs4 import BeautifulSoup

def get_pub_packages(word):
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

# 单独处理Flutter相关的包搜索
def search_flutter_packages(keywords, exact_match=True):
    pubdev_data = []
    
    # 对每个包名进行查询
    for kw in keywords:
        pub_results = get_pub_packages(kw)
        
        # 根据精准查询状态决定是否只取第一个结果
        if pub_results:
            if exact_match:
                pubdev_data.append(pub_results[0])  # 只添加第一个结果
            else:
                pubdev_data.extend(pub_results)  # 添加所有结果
    
    return pubdev_data