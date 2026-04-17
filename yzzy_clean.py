import re
from datetime import datetime

# -------------------------- 配置 --------------------------
M3U8_FILE = "yz.m3u8"
LOG_FILE = "m3u8_clean_log.txt"
OUTPUT_FILE = "cleaned.m3u8"
# -----------------------------------------------------------

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def clean_m3u8():
    with open(M3U8_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    log("=== 原始完整内容 ===")
    log(content)

    # ---------------- 去广告核心（专用修复） ----------------
    # 去开头广告 DISC → DISC
    pattern_head = re.compile(
        r'(#EXTM3U.*?)#EXT-X-DISCONTINUITY\s*\n(?:#EXTINF.*?\n.*?\n)+?#EXT-X-DISCONTINUITY\s*\n',
        re.S
    )
    content = pattern_head.sub(r'\1', content)

    # 去结尾广告 DISC → ENDLIST
    pattern_tail = re.compile(
        r'#EXT-X-DISCONTINUITY\s*\n(?:#EXTINF.*?\n.*?\n)+?#EXT-X-ENDLIST',
        re.S
    )
    content = pattern_tail.sub('#EXT-X-ENDLIST', content)
    # --------------------------------------------------------

    # 规整格式
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    content = "\n".join(lines)

    if not content.startswith("#EXTM3U"):
        content = "#EXTM3U\n" + content
    if "#EXT-X-ENDLIST" not in content:
        content += "\n#EXT-X-ENDLIST"

    log("\n=== 清理后完整内容 ===")
    log(content)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    log(f"\n✅ 完成！输出：{OUTPUT_FILE}")

if __name__ == "__main__":
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== M3U8 清理日志（全量输出） ===\n")
    clean_m3u8()
