import requests
import re
from urllib import parse
import sys
from datetime import datetime

# -------------------------- 配置区 --------------------------
URL = "https://cdn.yzzyvip-29.com/20260306/23075_0df840ae/2000k/hls/mixed.m3u8"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}
LOG_FILE = "m3u8_clean_log.txt"
OUTPUT_FILE = "cleaned.m3u8"
# -----------------------------------------------------------

def log(msg):
    """同时打印到控制台和日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def del_ads(url, headers):
    try:
        log(f"=== 开始处理URL: {url} ===")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            log(f"❌ 请求失败，状态码: {resp.status_code}")
            return '#EXTM3U\n#EXT-X-ENDLIST'
        
        log("✅ 成功获取原始m3u8内容")
        log(f"原始内容行数: {len(resp.text.splitlines())}")
        log("--- 原始m3u8内容 ---")
        log(resp.text[:500] + ("..." if len(resp.text) > 500 else "")) # 只打印前500字符，太长的话
        
        scheme = 'http'
        root = '/'
        base_url = url.rsplit(root, maxsplit=1)[0] + root
        parsed = parse.urlparse(url)
        base_host = parse.urlunparse([parsed.scheme, parsed.netloc, '', '', '', ''])
        
        lines = resp.text.splitlines()
        
        # 处理嵌套m3u8（递归）
        if len(lines) > 2 and lines[0] == '#EXTM3U' and 'mixed.m3u8' in lines[2]:
            log("🔍 检测到嵌套m3u8，准备递归处理...")
            if lines[2].startswith(scheme):
                next_url = lines[2]
            elif lines[2].startswith(root):
                next_url = base_host + lines[2]
            else:
                next_url = base_url + lines[2]
            return del_ads(next_url, headers)
        
        # 补全TS的URL，并记录DISCONTINUITY位置
        log("--- 开始补全TS路径 ---")
        new_lines = []
        disc_pos = []
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if '.ts' in line and not line.startswith('#'):
                if line.startswith(scheme):
                    new_lines.append(line)
                elif line.startswith(root):
                    new_lines.append(base_host + line)
                else:
                    new_lines.append(base_url + line)
            elif line == '#EXT-X-DISCONTINUITY':
                new_lines.append(line)
                disc_pos.append(len(new_lines) - 1)
            else:
                new_lines.append(line)
        
        log(f"✅ 补全后行数: {len(new_lines)}")
        log(f"✅ 检测到DISCONTINUITY标记数: {len(disc_pos)}，位置: {disc_pos}")
        log("--- 补全TS后的m3u8内容（前100行） ---")
        log('\n'.join(new_lines[:100]) + ("\n..." if len(new_lines) > 100 else ""))
        
        # 非凡的中间广告删除逻辑
        remove_ranges = []
        if len(disc_pos) >= 1:
            remove_ranges.append((disc_pos[0], disc_pos[0]))
        if len(disc_pos) >= 3:
            remove_ranges.append((disc_pos[1], disc_pos[2]))
        if len(disc_pos) >= 5:
            remove_ranges.append((disc_pos[3], disc_pos[4]))
        
        log(f"🔍 计算得到删除区间: {remove_ranges}")
        
        # 过滤掉中间广告
        final = []
        for idx, line in enumerate(new_lines):
            keep = True
            for (s, e) in remove_ranges:
                if s <= idx <= e:
                    keep = False
                    break
            if keep:
                final.append(line)
        
        log(f"✅ 中间广告删除后行数: {len(final)}")
        
        content = '\n'.join(final)
        
        # 正则删除结尾广告
        log("--- 开始删除结尾广告 ---")
        ad_pattern2 = re.compile(
            r'#EXT-X-DISCONTINUITY\s*\n(?:#EXTINF:.*?\n.*?\n){4,7}#EXT-X-ENDLIST',
            re.S
        )
        content = ad_pattern2.sub('#EXT-X-ENDLIST', content)
        
        # 确保有正确的头部和尾部
        if '#EXTM3U' not in content:
            content = '#EXTM3U\n' + content
        if '#EXT-X-ENDLIST' not in content:
            content = content + '\n#EXT-X-ENDLIST'
        
        # 清理多余空行
        content = re.sub(r'\n\s*\n', '\n', content)
        content = content.strip()
        
        log(f"✅ 最终处理完成，行数: {len(content.splitlines())}")
        log("--- 最终清理后的m3u8内容（前100行） ---")
        log(content[:2000] + ("\n..." if len(content) > 2000 else ""))
        
        return content if content else '#EXTM3U\n#EXT-X-ENDLIST'
        
    except Exception as e:
        log(f"❌ 处理出错: {e}")
        return '#EXTM3U\n#EXT-X-ENDLIST'

if __name__ == "__main__":
    # 清空日志文件
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== M3U8 去广告处理日志 ===\n")
    
    cleaned_content = del_ads(URL, HEADERS)
    
    # 写入最终文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(cleaned_content)
    
    log(f"\n🎉 处理完成！")
    log(f"日志文件: {LOG_FILE}")
    log(f"输出文件: {OUTPUT_FILE}")
    print("\n" + "="*50)
    print("你可以打开 m3u8_clean_log.txt 查看每一步的详细过程，对比原始/补全后/最终的内容差异。")
