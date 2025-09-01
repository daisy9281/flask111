import re
import requests
from bs4 import BeautifulSoup

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
    # 2. loop divs
    results = [["name", "version", "update_time"]]
    for package in packages.find_all('div', class_='packages-item'):
        res = []
        # get packages-header text
        header = package.find('div', class_='packages-header')
        #find h3/a in header
        h3 = header.find('h3')
        a = h3.find('a')
        res.append(a.text)
        # find span packages-metadata-block
        metadata = package.find('span', class_='packages-metadata-block')
        # find multi a
        a = metadata.find_all('a')
        res.append(a[0].text)
        res.append(a[1].text)
        results.append(res)
    return results

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
    results = []
    for section in sections:
        res = []
        # 1.find a target="_self"
        a = section.find('a', target="_self")
        if a is None:
            continue
        #find h3
        h3 = a.find('h3')
        res.append(h3.text)
        # 2.find span class iclass="_66c2abad flex-grow-1"
        span = section.find('span', class_="_66c2abad flex-grow-1")
        # span.text 删除非ascii字符
        span_text = span.text.encode('ascii', 'ignore').decode('ascii').split()
        version = span_text[0]
        others = " ".join(span_text[1:4])
        res.append(version)
        res.append(others)
        results.append(res)
    return results


def get_pubdev(word):
    try:
        results = get_zego_packages(word=word)
        print(results)
        # save tocsv
        filepath = f"/Users/zego/Desktop/zego_packages_pubdev_{word}.csv"
        with open(filepath, 'w') as f:
            lines = [",".join(x) for x in results]
            f.write("\n".join(lines))
        print(f"{filepath}...done")

    except Exception as e:
        print(f"获取pubdev失败: {e}")

def get_npmjs(word):
    try:
        results = get_npmjs_packages(word=word)
        print(results)
        # save tocsv
        filepath = f"/Users/zego/Desktop/zego_packages_npmjs_{word}.csv"
        with open(filepath, 'w') as f:
            lines = [",".join(x) for x in results]
            f.write("\n".join(lines))
        print(f"{filepath}...done")
    except Exception as e:
        print(f"获取npmjs失败: {e}")


if __name__ == "__main__":
    # read params:
    import sys
    if len(sys.argv) > 1:
        word = sys.argv[1]
    else:
        word = "zego"
    get_pubdev(word)
    get_npmjs(word)
