import re
from datetime import datetime

M3U8_FILE = "yz.m3u8"
LOG_FILE = "m3u8_clean_log.txt"
OUTPUT_FILE = "cleaned.m3u8"

def log(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

# 清空日志
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== 广告匹配调试日志 ===\n")

# 读取文件
with open(M3U8_FILE, "r", encoding="utf-8") as f:
    content = f.read()

log(f"原始总行数：{len(content.splitlines())}")

# ------------------- 你的广告正则 -------------------
pattern_mid = re.compile(
    r'#EXT-X-DISCONTINUITY\s*\n'
    r'(?:#EXTINF:\d+\.\d+,\s*\n.+?\n){4,7}'
    r'#EXT-X-DISCONTINUITY',
    re.S
)

pattern_end = re.compile(
    r'#EXT-X-DISCONTINUITY\s*\n'
    r'(?:#EXTINF:\d+\.\d+,\s*\n.+?\n){4,7}'
    r'#EXT-X-ENDLIST',
    re.S
)

# ------------------- 调试：查匹配到几条 -------------------
matches_mid = list(pattern_mid.finditer(content))
matches_end = list(pattern_end.finditer(content))

log(f"\n【中间广告匹配到】：{len(matches_mid)} 条")
for i, m in enumerate(matches_mid):
    log(f"  广告{i+1}：行 {m.start()}-{m.end()}")
    log(f"  内容预览：{m.group()[:200]}...\n")

log(f"\n【结尾广告匹配到】：{len(matches_end)} 条")
for i, m in enumerate(matches_end):
    log(f"  广告{i+1}：行 {m.start()}-{m.end()}")
    log(f"  内容预览：{m.group()[:200]}...\n")

# ------------------- 执行删除 -------------------
log("\n开始删除...")
content = pattern_mid.sub('', content)
content = pattern_end.sub('#EXT-X-ENDLIST', content)

# ------------------- 最终整理 -------------------
lines = [l.strip() for l in content.splitlines() if l.strip()]
content = "\n".join(lines)

if not content.startswith('#EXTM3U'):
    content = '#EXTM3U\n' + content

if '#EXT-X-ENDLIST' not in content:
    content += '\n#EXT-X-ENDLIST'

log(f"\n删除后总行数：{len(content.splitlines())}")

# 保存
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

log("\n完成！")
