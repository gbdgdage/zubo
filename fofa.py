import os
import re
import requests
import socket
import time

# ===============================
# 配置区（移除计数相关）
FOFA_URLS = {
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjb3VudHJ5PSJDTiI%3D": "ip.txt",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
IP_DIR = "ip"  # 仅保留IP目录，删除计数文件配置
# ===============================

# 运营商解析工具函数（保留）
def get_isp_from_api(data):
    isp_raw = (data.get("isp") or "").lower()
    if "telecom" in isp_raw or "ct" in isp_raw or "chinatelecom" in isp_raw:
        return "电信"
    elif "unicom" in isp_raw or "cu" in isp_raw or "chinaunicom" in isp_raw:
        return "联通"
    elif "mobile" in isp_raw or "cm" in isp_raw or "chinamobile" in isp_raw:
        return "移动"
    return "未知"

def get_isp_by_regex(ip):
    if re.match(r"^(1[0-9]{2}|2[0-3]{2}|42|43|58|59|60|61|110|111|112|113|114|115|116|117|118|119|120|121|122|123|124|125|126|127|175|180|182|183|184|185|186|187|188|189|223)\.", ip):
        return "电信"
    elif re.match(r"^(42|43|58|59|60|61|110|111|112|113|114|115|116|117|118|119|120|121|122|123|124|125|126|127|175|180|182|183|184|185|186|187|188|189|223)\.", ip):
        return "联通"
    elif re.match(r"^(223|36|37|38|39|100|101|102|103|104|105|106|107|108|109|134|135|136|137|138|139|150|151|152|157|158|159|170|178|182|183|184|187|188|189)\.", ip):
        return "移动"
    return "未知"

# 核心FOFA IP爬取逻辑（删除计数相关代码）
def fofa_crawl_ip():
    os.makedirs(IP_DIR, exist_ok=True)
    all_ips = set()
    # 爬取FOFA页面提取IP:PORT
    for url, filename in FOFA_URLS.items():
        print(f"📡 正在爬取 {filename} ...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            urls_all = re.findall(r'<a href="http://(.*?)"', r.text)
            all_ips.update(u.strip() for u in urls_all if u.strip())
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
        time.sleep(3)
    # 解析IP省份、运营商并分类
    province_isp_dict = {}
    for ip_port in all_ips:
        try:
            host = ip_port.split(":")[0]
            is_ip = re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host)
            # 域名解析为IP
            if not is_ip:
                try:
                    resolved_ip = socket.gethostbyname(host)
                    print(f"🌐 域名解析成功: {host} → {resolved_ip}")
                    ip = resolved_ip
                except Exception:
                    print(f"❌ 域名解析失败，跳过：{ip_port}")
                    continue
            else:
                ip = host
            # 调用ip-api获取省份运营商
            res = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=10)
            data = res.json()
            province = data.get("regionName", "未知")
            isp = get_isp_from_api(data)
            if isp == "未知":
                isp = get_isp_by_regex(ip)
            if isp == "未知":
                print(f"⚠️ 无法判断运营商，跳过：{ip_port}")
                continue
            fname = f"{province}{isp}.txt"
            province_isp_dict.setdefault(fname, set()).add(ip_port)
        except Exception as e:
            print(f"⚠️ 解析 {ip_port} 出错：{e}")
            continue
    # 写入IP文件（删除计数更新）
    for filename, ip_set in province_isp_dict.items():
        path = os.path.join(IP_DIR, filename)
        try:
            with open(path, "a", encoding="utf-8") as f:
                for ip_port in sorted(ip_set):
                    f.write(ip_port + "\n")
            print(f"{path} 已追加写入 {len(ip_set)} 个 IP")
        except Exception as e:
            print(f"❌ 写入 {path} 失败：{e}")
    print(f"✅ FOFA IP爬取完成，所有IP已写入 {IP_DIR}/ 目录")

# 主入口
if __name__ == "__main__":
    fofa_crawl_ip()
