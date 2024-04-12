import requests
from bs4 import BeautifulSoup

# 发送GET请求获取Firefox下载页面的HTML内容
url = "https://download.mozilla.org/?product=firefox-latest&os=Win&lang=zh-CN"
response = requests.get(url)

# 检查响应状态码
if response.status_code == 200:
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # 根据HTML结构查找包含版本号的元素
    # 这里需要根据实际页面的HTML结构来确定如何提取版本号
    # 例如，假设版本号位于页面的某个<meta>标签中，名称为"version"
    version_meta = soup.find("meta", attrs={"name": "version"})
    
    if version_meta:
        # 提取版本号
        version = version_meta["content"]
        print(f"Firefox version: {version}")
    else:
        print("Version information not found.")
else:
    print("Failed to retrieve the download page.")
