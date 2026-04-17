import requests
import re
from urllib import parse
import sys
from datetime import datetime

# -------------------------- 配置区 --------------------------
# 不从远程拉，直接读 GitHub 同目录下的 yz.m3u8
M3U8_FILE = "yz.m3u8"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}
LOG_FILE = "m3u8_clean_log.txt"
OUTPUT_FILE = "cleaned.m3u8"
# -----------------------------------------------------------

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def del_ads_from_file(file_path):
    try:
        log(f"=== 从本地文件读取: {file_path} ===")
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        log("✅ 成功读取本地 m3u8")
        log(f"原始总行数: {len(raw_text.splitlines())}")
        log("--- 完整原始 m3u8 内容 ---")
        log(raw_text)  # 输出全部，不截断

        scheme = 'http'
        root = '/'
        base_url = "https://cdn.yzzyvip-29.com/20260306/23075_0df840ae/2000k/hls/"
        base_host = "https://cdn.yzzyvip-29.com"

        lines = raw_text.splitlines()

        # 补全TS路径
        log("--- 开始补全 TS 路径 ---")
        new_lines = []
        disc_pos = []
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if '.ts' in line and not line.startswith('#'):
                if line.startswith('http'):
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

        log(f"✅ 补全后总行数: {len(new_lines)}")
        log(f"✅ DISCONTINUITY 位置: {disc_pos}")
        log("--- 补全后完整内容 ---")
        log('\n'.join(new_lines))  # 输出全部

        # 拼接
        content = '\n'.join(new_lines)

        # ------------ 你要的 正则去中间广告 ------------
        log("--- 开始用正则删除中间广告 ---")
        pattern_mid = re.compile(
            r'#EXT-X-DISCONTINUITY\s*\n(?:#EXTINF:.*?\n.*?\n){4,7}\s*#EXT-X-DISCONTINUITY',
            re.S | re.M
        )
        content = pattern_mid.sub('', content)
        log("✅ 中间广告正则删除完成")

        # 再清理空行
        lines_clean = [l.strip() for l in content.splitlines() if l.strip()]
        content = '\n'.join(lines_clean)

        # ------------ 删除结尾广告 ------------
        log("--- 开始删除结尾广告 ---")
        ad_pattern2 = re.compile(
            r'#EXT-X-DISCONTINUITY\s*\n(?:#EXTINF:.*?\n.*?\n){4,7}#EXT-X-ENDLIST',
            re.S
        )
        content = ad_pattern2.sub('#EXT-X-ENDLIST', content)

        # 保证头尾
        if not content.startswith('#EXTM3U'):
            content = '#EXTM3U\n' + content
        if '#EXT-X-ENDLIST' not in content:
            content += '\n#EXT-X-ENDLIST'

        # 最终清理
        content = re.sub(r'\n+', '\n', content).strip()

        log(f"✅ 最终总行数: {len(content.splitlines())}")
        log("--- 最终完整清理结果 ---")
        log(content)  # 输出全部

        return content

    except Exception as e:
        log(f"❌ 出错: {e}")
        return '#EXTM3U\n#EXT-X-ENDLIST'

if __name__ == "__main__":
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== M3U8 去广告调试日志（全输出） ===\n")

    final_content = del_ads_from_file(M3U8_FILE)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)

    log("\n🎉 处理完成！")
    log(f"日志: {LOG_FILE}")
    log(f"清理后: {OUTPUT_FILE}")
