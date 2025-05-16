from github import Github
import requests
import base64
import json
import time
import socket
import geoip2.database
import os
import tempfile
from github import Auth


# 示例（替换为你的 GeoLite2 下载链接）
GEOIP_DB_URL = "https://git.io/GeoLite2-City.mmdb"  # 需提供可下载的 URL
def load_geolite2_tempfile(url):
    """下载到临时文件再加载"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        reader = geoip2.database.Reader(tmp_path)
        os.unlink(tmp_path)  # 删除临时文件
        return reader
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise ValueError(f"加载失败: {e}")
    
def get_country(ip):
    tryMax = 5
    country = ""
    while tryMax > 0:
        tryMax -= 1
        try:
            r = requests.get(f"https://ipapi.co/{ip}/json/")
            if r.status_code == 200:
                country = json.loads(r.text)["country"]
                print(country)
                break
        except Exception as e:
            print(e)
        time.sleep(5)
    return country
def resolve_domain(domain):
    try:
        # 获取 IPv4 地址
        ip = socket.gethostbyname(domain)
        return {"scuss": True, "ip": ip}
    except socket.gaierror as e:
        return {"scuss": False, "ip": f"解析失败: {e}"}

def get_country_by_ip(ip):
    reader = load_geolite2_tempfile(GEOIP_DB_URL)
    response = reader.city(str(ip))
    country = response.country.iso_code
    # 关闭 reader（释放内存）
    reader.close()
    return country
urls = ''
url = "https://jmssub.net/members/getsub.php?service=1036510&id=c4aff60b-1ad6-4ee4-84ed-1a55c3cae4b8"
response = requests.get(url)
# base64解码
response = base64.b64decode(response.text)
# 转换为字符串
# r = requests.get("https://api.ipshudi.com/query/?ip=45.78.59.148&oid=5&mid=5&from=siteFront&datatype=jsonp&sign=526d7c18feb6249cb6f00d0b921dbd93&callback=jsonp_06465841737099244")
# print(r.text)
proxies = response.decode('utf-8')
# print(proxies.split('\n'))
for p in proxies.split('\n'):
    print(p)
    ip = '223.5.5.5'
    if p.startswith('ss'):
        domain = p.split('@')[-1].split(':')[0]
        # 解析域名为ip
        rip = resolve_domain(domain)
        if rip["scuss"]:
            ip = rip["ip"]
            # country = get_country(ip["ip"])
            urls += p.split('#')[0] + "#" + ip
        # country = get_country(ip)
    elif p.startswith('vmess'):
        pb = p.split('://')[1]
        padding_needed = len(pb) % 4
        if padding_needed:
            pb += "=" * (4 - padding_needed)
        pd = base64.b64decode(pb).decode('utf-8')
        vmess = json.loads(pd)
        ip = vmess['add']
        vmess['ps'] = ip
        print(vmess)
        # vmess转为bytes-like object
        vmess = json.dumps(vmess)
        urls += "vmess://" + base64.b64encode(vmess.encode("utf-8")).decode("utf-8")
        # country = get_country(vmess['add'])
    # 查询 IP
    
    # print(f"Country: {response.country.name}, City: {response.city.name}")
print(urls)
dingyue = base64.b64encode(urls.encode("utf-8")).decode("utf-8")
print(dingyue)
auth = Auth.Token("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")
g = Github(auth=auth)
repo = g.get_repo("Klaus-Arroyo-Zeng/autoupdatejustmystocks")
file = repo.get_contents("config")  # 如 "data/config.txt"

# 更新文件
repo.update_file(
    path=file.path,
    message="Update via PyGithub",
    content=dingyue,
    sha=file.sha  # 必须提供
)
