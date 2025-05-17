import requests
import base64
import json
import time
import socket
import geoip2.database
import os
import tempfile


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
urls = []
subscribe = [
    "https://jmssub.net/members/getsub.php?service=1036510&id=c4aff60b-1ad6-4ee4-84ed-1a55c3cae4b8",
    "https://jmssub.net/members/getsub.php?service=1036512&id=eb015ce0-0d40-4d18-8cd0-7aec8f1c6002",
    "https://jmssub.net/members/getsub.php?service=1036511&id=86239d05-c5c3-45a5-8e80-06fe5c4ff55e",
]
proxies = []
for url in subscribe:
    maxTry = 5
    while maxTry > 0 :
        try:
            response = requests.get(url)
        except Exception as e:
            print(e)
        maxTry -=1
    # base64解码
    response = base64.b64decode(response.text)
    p = response.decode('utf-8').split('\n')
    proxies = [*proxies,*p]
reader = load_geolite2_tempfile(GEOIP_DB_URL)
# print(proxies.split('\n'))
for p in proxies:
    print(p)
    ip = '223.5.5.5'
    if p.startswith('ss'):
        domain = p.split('@')[-1].split(':')[0]
        # 解析域名为ip
        rip = resolve_domain(domain)
        if rip["scuss"]:
            ip = rip["ip"]
            # country = get_country(ip["ip"])
            response = reader.city(str(ip))
            country = response.country.iso_code
            urls.append(p.split('#')[0] + "#" + country)
        # country = get_country(ip)
    elif p.startswith('vmess'):
        pb = p.split('://')[1]
        padding_needed = len(pb) % 4
        if padding_needed:
            pb += "=" * (4 - padding_needed)
        pd = base64.b64decode(pb).decode('utf-8')
        vmess = json.loads(pd)
        ip = vmess['add']
        response = reader.city(str(ip))
        country = response.country.iso_code
        vmess['ps'] = country
        print(vmess)
        # vmess转为bytes-like object
        vmess = json.dumps(vmess)
        urls.append("vmess://" + base64.b64encode(vmess.encode("utf-8")).decode("utf-8"))
        # country = get_country(vmess['add'])
    # 查询 IP
    
    # print(f"Country: {response.country.name}, City: {response.city.name}")
print(urls)
urls_str = "\n".join(urls)
print(urls_str)
dingyue = base64.b64encode(urls_str.encode("utf-8")).decode("utf-8")
print(dingyue)

with open("config", "w") as f:
    f.write(dingyue)
