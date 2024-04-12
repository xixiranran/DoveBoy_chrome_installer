import requests

url = "https://download.mozilla.org/?product=firefox-latest&os=Win&lang=zh-CN"
response = requests.get(url)

print(response)
# 检查响应状态码
if response.status_code == 200:
    # 处理响应内容，获取下载链接
    download_link = response.version
    print(download_link)
else:
    print("Failed to retrieve the download link.")
