import requests
import xml.etree.ElementTree as tree
import base64
import binascii
import json
from datetime import datetime, timezone

info = {
    "win_stable_x86": {
        "os": '''platform="win" version="10.0" sp="" arch="x86"''',
        "app": '''appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" version="" nextversion="" lang="en" brand=""  installage="-1" installdate="-1" iid="{11111111-1111-1111-1111-111111111111}"''',
    },
    "win_stable_x64": {
        "os": '''platform="win" version="10.0" sp="" arch="x64"''',
        "app": '''appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" version="" nextversion="" lang="en" brand=""  installage="-1" installdate="-1" iid="{11111111-1111-1111-1111-111111111111}"''',
    },
    "win_beta_x86": {
        "os": '''platform="win" version="10.0" arch="x86"''',
        "app": '''appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" ap="1.1-beta"''',
    },
    "win_beta_x64": {
        "os": '''platform="win" version="10.0" arch="x64"''',
        "app": '''appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" ap="x64-beta-multi-chrome"''',
    },
    "win_dev_x86": {
        "os": '''platform="win" version="10.0" arch="x86"''',
        "app": '''appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" ap="2.0-dev"''',
    },
    "win_dev_x64": {
        "os": '''platform="win" version="10.0" arch="x64"''',
        "app": '''appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" ap="x64-dev-multi-chrome"''',
    },
    "win_canary_x86": {
        "os": '''platform="win" version="10.0" arch="x86"''',
        "app": '''appid="{4EA16AC7-FD5A-47C3-875B-DBF4A2008C20}" ap="x86-canary"''',
    },
    "win_canary_x64": {
        "os": '''platform="win" version="10.0" arch="x64"''',
        "app": '''appid="{4EA16AC7-FD5A-47C3-875B-DBF4A2008C20}" ap="x64-canary"''',
    },
    "mac_stable": {
        "os": '''platform="mac" version="46.0.2490.86" arch="x64"''',
        "app": '''appid="com.google.Chrome" ap=""''',
    },
    "mac_beta": {
        "os": '''platform="mac" version="46.0.2490.86" arch="x64"''',
        "app": '''appid="com.google.Chrome" ap="betachannel"''',
    },
    "mac_dev": {
        "os": '''platform="mac" version="46.0.2490.86" arch="x64"''',
        "app": '''appid="com.google.Chrome" ap="devchannel"''',
    },
    "mac_canary": {
        "os": '''platform="mac" version="46.0.2490.86" arch="x64"''',
        "app": '''appid="com.google.Chrome.Canary" ap=""''',
    },
}

update_url = 'https://tools.google.com/service/update2'

session = requests.Session()


def post(os: str, app: str) -> str:
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <request protocol="3.0" updater="Omaha" updaterversion="1.3.36.372" shell_version="1.3.36.352" ismachine="0" sessionid="{11111111-1111-1111-1111-111111111111}" installsource="taggedmi" requestid="{11111111-1111-1111-1111-111111111111}" dedup="cr" domainjoined="0">
    <hw physmemory="16" sse="1" sse2="1" sse3="1" ssse3="1" sse41="1" sse42="1" avx="1"/>
    <os {os}/>
    <app {app}>
    <updatecheck/>
    <data name="install" index="empty"/>
    </app>
    </request>'''
    r = session.post(update_url, data=xml)
    return r.text

def decode(text):

    root = tree.fromstring(text)

    manifest_node = root.find('.//manifest')
    manifest_version = manifest_node.get('version')
    
    package_node = root.find('.//package')
    package_name = package_node.get('name')
    package_size = int(package_node.get('size'))
    package_sha1 = package_node.get('hash')
    package_sha1 = base64.b64decode(package_sha1)
    package_sha1 = package_sha1.hex()
    package_sha256 = package_node.get('hash_sha256')

    url_nodes = root.findall('.//url')
    url_prefixes = []
    for node in url_nodes:
        url_prefixes.append(node.get('codebase') + package_name)

    return {"version":manifest_version, "size":package_size, "sha1":package_sha1, "sha256":package_sha256, "urls":url_prefixes}

results = {}

def version_tuple(v):
    return tuple(map(int, (v.split("."))))

def load_json():
    global results
    with open('data.json', 'r') as f:
        results = json.load(f)

def fetch():
    for k, v in info.items():
        res = post(**v)
        data = decode(res)
        if "stable" in k:
            data['label'] = 'Stable 稳定版'
        elif "beta" in k:
            data['label'] = 'Beta 测试版'
        elif "dev" in k:
            data['label'] = 'Dev 开发版'
        elif "canary" in k:
           data['label']= 'Canary 金丝雀版'
        #print("k:",k)
        #print("v:",v)
        #print("info:",info)
        #print("info.items():",info.items())
        #print("res:",res)
        #print("data:",data)
        if version_tuple(data['version']) < version_tuple(results[k]['version']):
            print("ignore", k, data['version'])
            continue
        results[k] = data

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def save_md():
    with open('readme.md', 'w') as f:
        f.write(f'# Automatic Generated Time\n')
        f.write(f'{datetime.now(timezone.utc)}\n')
        f.write('\n')
        for k, v in results.items():
            #f.write(f'## {k.replace("_", " ")}\n')
            print("k:",k)
            print("v:",v)
            print("results:",results)
            print("results.items():",results.items())
            #f.write(f'## {v["label"]}  \n')
            f.write(f'**version**:{v["version"]}  \n')
            f.write(f'**size**:{humansize(v["size"])}  \n')
            f.write(f'**sha1**:{v["sha1"]}  \n')
            f.write(f'**sha256**:{v["sha256"]}  \n')
            f.write(f'**download**:  \n')
            for url in v["urls"]:
                if url.startswith("http"):
                    f.write(f'[{url}]({url})  \n')

            f.write('\n')

def save_json():
    with open('data.json', 'w') as f:
        json.dump(results, f, indent=4)
    for k, v in results.items():
        with open(f'{k}.json', 'w') as f:
            json.dump(v, f, indent=4)

def main():
    load_json()
    fetch()
    save_md()
    save_json()

main()
