import requests
from bs4 import BeautifulSoup

def get_npm_packages(word):
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

# 单独处理React Native相关的包搜索
def search_npm_packages(keywords, exact_match=True):
    npmjs_data = []
    
    # 对每个包名进行查询
    for kw in keywords:
        npm_results = get_npm_packages(kw)
        
        # 根据精准查询状态决定是否只取第一个结果
        if npm_results:
            if exact_match:
                npmjs_data.append(npm_results[0])  # 只添加第一个结果
            else:
                npmjs_data.extend(npm_results)  # 添加所有结果
    
    return npmjs_data