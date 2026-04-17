import re
from datetime import datetime

# 配置
M3U8_FILE = "yz.m3u8"
LOG_FILE = "m3u8_clean_log.txt"
OUTPUT_FILE = "cleaned.m3u8"

# 日志函数（只输出关键步骤）
def log(text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

# 清空日志
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== 去广告调试日志（仅记录关键步骤） ===\n")

# 读取本地文件
with open(M3U8_FILE, "r", encoding="utf-8") as f:
    content = f.read()

log("✅ 读取 yz.m3u8 完成")
log("==================== 开始去广告 ====================")

# ===================== 去广告规则（你的核心逻辑） =====================
# 1. 中间广告：DISC 包裹 4-7 个 TS
pattern_mid = re.compile(
    r'#EXT-X-DISCONTINUITY\s*\n'
    r'(?:#EXTINF:\d+\.\d+,\s*\n.+?\n){4,7}'
    r'#EXT-X-DISCONTINUITY',
    re.S
)

# 2. 结尾广告：DISC 到 ENDLIST 4-7 个 TS
pattern_end = re.compile(
    r'#EXT-X-DISCONTINUITY\s*\n'
    r'(?:#EXTINF:\d+\.\d+,\s*\n.+?\n){4,7}'
    r'#EXT-X-ENDLIST',
    re.S
)

# ===================== 调试：每一步都打日志 =====================
log("📌 去广告前内容（前50行）：")
log("\n".join(content.splitlines()[:50]))

# 第一次删中间广告
log("\n🔍 执行第一次删除中间广告...")
content1 = pattern_mid.sub('', content)
log(f"✅ 删除后行数：原始={len(content.splitlines())} → 删后={len(content1.splitlines())}")

# 第二次删中间广告（最多删3段）
log("\n🔍 执行第二次删除中间广告...")
content2 = pattern_mid.sub('', content1)
log(f"✅ 删除后行数：{len(content1.splitlines())} → {len(content2.splitlines())}")

# 第三次删中间广告
log("\n🔍 执行第三次删除中间广告...")
content3 = pattern_mid.sub('', content2)
log(f"✅ 删除后行数：{len(content2.splitlines())} → {len(content3.splitlines())}")

# 删除结尾广告
log("\n🔍 执行删除结尾广告...")
final_content = pattern_end.sub('#EXT-X-ENDLIST', content3)
log(f"✅ 结尾清理后行数：{len(content3.splitlines())} → {len(final_content.splitlines())}")

# ===================== 最后规整 =====================
log("\n📌 开始规整 m3u8 结构...")

lines = [l.strip() for l in final_content.splitlines() if l.strip()]
final_content = "\n".join(lines)

if not final_content.startswith('#EXTM3U'):
    final_content = '#EXTM3U\n' + final_content

if '#EXT-X-ENDLIST' not in final_content:
    final_content += '\n#EXT-X-ENDLIST'

log(f"✅ 最终总行数：{len(final_content.splitlines())}")

# 输出最终内容
log("\n==================== 最终清理结果 ====================")
log(final_content)

# 保存文件
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(final_content)

log(f"\n🎉 处理完成！清理结果保存到 {OUTPUT_FILE}")
