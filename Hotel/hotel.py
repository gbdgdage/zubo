import os
import re
import datetime
import requests
from urllib3.exceptions import InsecureRequestWarning
# 禁用不安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# ====================== 配置区======================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
IP_DIR = "Hotel/ip"
if not os.path.exists(IP_DIR):
    os.makedirs(IP_DIR)

CHANNEL_CATEGORIES = {
    "央视频道": [
        "CCTV1", "CCTV2", "CCTV3", "CCTV4", "CCTV5", "CCTV5+", "CCTV6", "CCTV7",
        "CCTV8", "CCTV9", "CCTV10", "CCTV11", "CCTV12", "CCTV13", "CCTV14", "CCTV15", "CCTV16", "CCTV17",
        "兵器科技", "风云音乐", "风云足球", "风云剧场", "怀旧剧场", "第一剧场", "女性时尚", "世界地理", "央视台球", "高尔夫网球",
    ],
    "卫视频道": [
        "湖南卫视", "浙江卫视", "江苏卫视", "东方卫视", "深圳卫视", "北京卫视", "广东卫视", "广西卫视", "东南卫视",
        "河北卫视", "河南卫视", "湖北卫视", "四川卫视", "重庆卫视", "贵州卫视", "云南卫视", "天津卫视", "安徽卫视",
        "山东卫视", "辽宁卫视", "黑龙江卫视", "吉林卫视", "内蒙古卫视", "山西卫视", "陕西卫视",
    ],
    "数字频道": [
        "CHC动作电影", "CHC家庭影院", "CHC影迷电影", "淘电影", "淘剧场", "淘娱乐",
        "IPTV热播剧场","IPTV谍战剧场", "IPTV戏曲","IPTV经典电影", "IPTV喜剧影院", "IPTV动作影院", "精品剧场","IPTV抗战剧场", 
    ],
}
SPECIAL_SYMBOLS = ["HD", "LT", "XF", "-", "_", " ", ".", "·", "高清", "标清", "超清", "H265", "4K", "FHD", "HDTV", "测试"]
RESULTS_PER_CHANNEL = 50  # 单频道保留的最大地址数

CHANNEL_MAPPING = {
    "CCTV1": ["CCTV1", "CCTV-1", "CCTV1综合", "CCTV1高清", "CCTV1HD", "cctv1", "中央1台", "CCTV01"],
    "CCTV2": ["CCTV2", "CCTV-2", "CCTV2财经", "CCTV2高清", "CCTV2HD", "cctv2", "中央2台", "CCTV02"],
    "CCTV3": ["CCTV3", "CCTV-3", "CCTV3综艺", "CCTV3高清", "CCTV3HD", "cctv3", "中央3台", "CCTV03"],
    "CCTV4": ["CCTV4", "CCTV-4", "CCTV4中文国际", "CCTV4-国际", "CCTV4高清", "CCTV4HD", "cctv4", "中央4台", "CCTV04"],
    "CCTV5": ["CCTV5", "CCTV-5", "CCTV5体育", "CCTV5高清", "CCTV5HD", "cctv5", "中央5台", "CCTV05"],
    "CCTV5+": ["CCTV5+", "CCTV-5+", "CCTV5+体育赛事", "CCTV5+高清", "CCTV5+HD", "cctv5+", "CCTV5plus"],
    "CCTV6": ["CCTV6", "CCTV-6", "CCTV6电影", "CCTV6高清", "CCTV6HD", "cctv6", "中央6台", "CCTV06"],
    "CCTV7": ["CCTV7", "CCTV-7", "CCTV7军事", "CCTV7高清", "CCTV7-军农", "CCTV7HD", "cctv7", "中央7台", "CCTV07", "CCTV7国防军事"],
    "CCTV8": ["CCTV8", "CCTV-8", "CCTV8电视剧", "CCTV8高清", "CCTV8HD", "cctv8", "中央8台", "CCTV08"],
    "CCTV9": ["CCTV9", "CCTV-9", "CCTV9纪录", "CCTV9高清", "CCTV9HD", "cctv9", "中央9台", "CCTV09"],
    "CCTV10": ["CCTV10", "CCTV-10", "CCTV10科教", "CCTV10高清", "CCTV10HD", "cctv10", "中央10台"],
    "CCTV11": ["CCTV11", "CCTV-11", "CCTV11戏曲", "CCTV11高清", "CCTV11HD", "cctv11", "中央11台"],
    "CCTV12": ["CCTV12", "CCTV-12", "CCTV12社会与法", "CCTV12高清", "CCTV12HD", "cctv12", "中央12台"],
    "CCTV13": ["CCTV13", "CCTV-13", "CCTV13新闻", "CCTV13高清", "CCTV13HD", "cctv13", "中央13台", "CCTV-新闻"],
    "CCTV14": ["CCTV14", "CCTV-14", "CCTV14少儿", "CCTV14高清", "CCTV14HD", "cctv14", "中央14台", "CCTV-少儿"],
    "CCTV15": ["CCTV15", "CCTV-15", "CCTV15音乐", "CCTV15高清", "CCTV15HD", "cctv15", "中央15台", "CCTV-音乐"],
    "CCTV16": ["CCTV16", "CCTV-16", "CCTV16奥林匹克", "CCTV16高清", "CCTV16HD", "cctv16", "中央16台"],
    "CCTV17": ["CCTV17", "CCTV-17", "CCTV17农业农村", "CCTV17高清", "CCTV17HD", "cctv17", "中央17台"],
    "湖南卫视": ["湖南卫视", "湖南电视", "湖南卫视高清"],
    "浙江卫视": ["浙江卫视高清"],
    "江苏卫视": ["江苏卫视HD", "江苏卫视高清"],
    "东方卫视": ["上海卫视", "东方卫视"],
    "深圳卫视": ["深圳卫视高清", "深圳卫视"],
    "北京卫视": ["北京卫视HD", "北京卫视高清"],
    "广东卫视": ["广东卫视", "广东卫视高清"],
    "广西卫视": ["广西卫视", "广西卫视高清"],
    "东南卫视": ["福建东南", "东南卫视"],
    "河北卫视": ["河北卫视", "河北卫视高清"],
    "河南卫视": ["河南卫视", "河南卫视高清"],
    "湖北卫视": ["湖北卫视", "湖北卫视高清"],
    "四川卫视": ["四川卫视", "四川卫视高清"],
    "重庆卫视": ["重庆卫视", "重庆卫视高清"],
    "贵州卫视": ["贵州卫视", "贵州卫视高清"],
    "云南卫视": ["云南卫视", "云南卫视高清"],
    "天津卫视": ["天津卫视", "天津卫视高清"],
    "安徽卫视": ["安徽卫视高清"],
    "山东卫视": ["山东卫视", "山东卫视高清", "山东卫视HD"],
    "辽宁卫视": ["辽宁卫视HD", "辽宁卫视 高清"],
    "黑龙江卫视": ["黑龙江卫视高清"],
    "吉林卫视": ["吉林卫视", "吉林卫视高清"],
    "内蒙古卫视": ["内蒙古卫视高清", "内蒙古"],
    "山西卫视": ["山西卫视高清"],
    "陕西卫视": ["陕西卫视"],
    "兵器科技": ["兵器科技", "CCTV兵器科技", "兵器科技频道","兵器科技HD",],
    "风云音乐": ["风云音乐", "CCTV风云音乐","风云音乐高清"],
    "第一剧场": ["第一剧场", "CCTV第一剧场","第一剧场HD",],
    "风云足球": ["风云足球", "CCTV风云足球","风云足球HD","风云足球高清"],
    "风云剧场": ["风云剧场", "CCTV风云剧场","风云剧场HD","风云剧场高清"],
    "怀旧剧场": ["怀旧剧场", "CCTV怀旧剧场","怀旧剧场HD",],
    "女性时尚": ["女性时尚", "CCTV女性时尚"],
    "世界地理": ["地理世界", "CCTV世界地理","世界地理高清"],
    "央视台球": ["央视台球", "CCTV央视台球","央视台球HD",],
    "高尔夫网球": ["高尔夫网球", "央视高网", "CCTV高尔夫网球", "高尔夫","高尔夫·网球HD",],
    "CHC动作电影": ["动作电影","CHC 动作电影",],
    "CHC家庭影院": ["家庭影院","CHC 家庭影院",],
    "CHC影迷电影": ["高清电影","CHC 高清电影",],
    "淘电影": ["淘电影", "IPTV淘电影"],
    "淘剧场": ["淘剧场", "IPTV淘剧场"],
    "淘娱乐": ["淘娱乐", "IPTV淘娱乐"],
    "IPTV戏曲": ["相声小品",],
    "IPTV热播剧场": ["IPTV-热播剧场","热播剧场"],
    "IPTV谍战剧场": ["IPTV-谍战剧场","谍战剧场"],
    "IPTV经典电影": ["经典电影", "IPTV-经典电影"],
    "IPTV喜剧影院": ["喜剧影院", "IPTV-喜剧影院"],
    "IPTV动作影院": ["动作影院", "IPTV-动作影院"],
    "IPTV抗战剧场": ["测试频道15","抗战剧场","IPTV-抗战剧场"],
    "精品剧场": ["精品剧场", "IPTV精品剧场"],
}

# ====================== 工具函数 ======================
def remove_special_symbols(text):
    for symbol in SPECIAL_SYMBOLS:
        text = text.replace(symbol, "")
    return re.sub(r'\s+', '', text).strip().lower()

def process_channels(all_channels):
    # 初始化分类字典，自动适配CHANNEL_CATEGORIES
    itv_dict = {cat: [] for cat in CHANNEL_CATEGORIES}
    # 遍历原始频道，统一名称并分类
    for name, channel_url in all_channels:
        # 过滤海外/衍生关键词
        if any(key in name for key in ["欧洲", "美洲", "NEWS", "电视指南"]):
            continue
        # 匹配标准频道名称
        std_name = None
        clean_name = remove_special_symbols(name)
        for _std, aliases in CHANNEL_MAPPING.items():
            if clean_name in [remove_special_symbols(alias) for alias in aliases]:
                std_name = _std
                break
        # 匹配到标准名后，按分类归类
        if std_name:
            for cat, channels in CHANNEL_CATEGORIES.items():
                if std_name in channels:
                    itv_dict[cat].append((std_name, channel_url))
                    break
    # 去重（按 频道名+IP 去重）
    def deduplicate(channels):
        seen = set()
        unique = []
        for n, u in channels:
            ip = u.split("//")[1].split("/")[0]
            key = (n, ip)
            if key not in seen:
                seen.add(key)
                unique.append((n, u))
        return unique
    # 对各分类去重
    for cat in itv_dict:
        itv_dict[cat] = deduplicate(itv_dict[cat])
    return itv_dict

# ====================== IP访问与频道提取======================
def check_single_ip(ip_port, url_end):
    try:
        url = f"http://{ip_port}{url_end}"
        resp = requests.get(url, timeout=3, headers=HEADERS, verify=False)
        resp.raise_for_status()
        if "tsfile" in resp.text or "hls" in resp.text or "m3u8" in resp.text:
            print(f"{url} 访问成功")
            return url
    except:
        return None

def extract_channels(url):
    hotel_channels = []
    try:
        urls = url.split('/', 3)
        url_x = f"{urls[0]}//{urls[2]}"
        current_ip_port = urls[2]
        if "ZHGXTV" in url:
            response = requests.get(url, timeout=2, headers=HEADERS, verify=False)
            json_data = response.content.decode('utf-8')
            for line in json_data.split('\n'):
                line = line.strip()
                if not line or "," not in line:
                    continue
                if "hls" in line or "m3u8" in line:
                    name, channel_url = line.split(',', 1)
                    channel_url = re.sub(r'(\d+\.\d+\.\d+\.\d+)(:\d+)?/', f'{current_ip_port}/', channel_url)
                    hotel_channels.append((name.strip(), channel_url.strip()))
        elif "iptv" in url:
            response = requests.get(url, timeout=3, headers=HEADERS, verify=False)
            json_data = response.json()
            for item in json_data.get('data', []):
                if isinstance(item, dict):
                    name = item.get('name', '').strip()
                    urlx = item.get('url', '').strip()
                    if name and urlx and ("tsfile" in urlx or "m3u8" in urlx):
                        if not urlx.startswith('/'):
                            urlx = '/' + urlx
                        urld = f"{url_x}{urlx}"
                        hotel_channels.append((name, urld))
        return hotel_channels
    except Exception as e:
        print(f"解析频道错误 {url}: {str(e)[:30]}")
        return []

# ====================== 主流程======================
def hotel_iptv():
    try:
        ip_file = os.path.join(IP_DIR, "hotel_ip.txt")
        if not os.path.exists(ip_file):
            print(f"错误：未找到 {ip_file}")
            return
        with open(ip_file, 'r', encoding='utf-8') as f:
            ip_ports = [line.strip() for line in f if line.strip()]
        if not ip_ports:
            print("警告：IP 文件为空")
            return
        print(f"✅ 读取到 {len(ip_ports)} 个有效 IP，开始访问")
        
        valid_urls = []
        url_ends = ["/iptv/live/1000.json?key=txiptv", "/ZHGXTV/Public/json/live_interface.txt"]
        for ip_port in ip_ports:
            for url_end in url_ends:
                url = check_single_ip(ip_port, url_end)
                if url:
                    valid_urls.append(url)
        
        if not valid_urls:
            print("⚠️ 未扫描到有效频道URL")
            return
        print(f"✅ 共扫描到 {len(valid_urls)} 个有效URL")
        
        all_channels = []
        for url in valid_urls:
            all_channels.extend(extract_channels(url))
        
        if not all_channels:
            print("⚠️ 未提取到任何频道")
            return
        print(f"✅ 共提取到 {len(all_channels)} 个原始频道（无测速）")
        
        # 处理频道（统一名称+分类+去重）
        categorized_channels = process_channels(all_channels)
        
        # 检查是否有有效频道
        if not any(categorized_channels.values()):
            print("⚠️ 无有效标准频道可输出")
            return
        
        # 北京时间
        import pytz
        beijing_tz = pytz.timezone("Asia/Shanghai")
        current_time = datetime.datetime.now(beijing_tz).strftime("%Y/%m/%d %H:%M")
        
        output_dir = "Hotel"
        os.makedirs(output_dir, exist_ok=True)
        final_output = os.path.join(output_dir, "hotel.txt")
        
        # 动态遍历CHANNEL_CATEGORIES输出，自动适配配置修改
        with open(final_output, "w", encoding='utf-8') as f_out:
            f_out.write(f"{current_time}更新\n\n")
            for cat in CHANNEL_CATEGORIES:
                f_out.write(f"{cat},#genre#\n")
                # 按配置里的频道顺序遍历，保证输出顺序和配置一致
                for ch in CHANNEL_CATEGORIES[cat]:
                    ch_items = [x for x in categorized_channels[cat] if x[0] == ch]
                    ch_items = ch_items[:RESULTS_PER_CHANNEL]  # 限制单频道地址数
                    for item in ch_items:
                        f_out.write(f"{item[0]},{item[1]}\n")
                f_out.write("\n")  # 分类间空行分隔
        
        # 统计打印
        print(f"\n🎉 处理完成！最终文件已保存到: {final_output}")
    except Exception as e:
        print(f"❌ 整体处理失败: {str(e)}")

def main():
    # 主函数
    hotel_iptv()
    
    print("📌 输出hotel.txt")

if __name__ == "__main__":
    main()
