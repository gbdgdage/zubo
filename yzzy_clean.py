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
    f.write("=== 精准去广告调试日志 ===\n")

# 读取并按行处理（保留原始换行）
with open(M3U8_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

log(f"原始总行数：{len(lines)}")

# 1. 找到所有DISCONTINUITY的行号
disc_lines = []
for i, line in enumerate(lines):
    if line.strip() == "#EXT-X-DISCONTINUITY":
        disc_lines.append(i)

log(f"✅ 找到DISCONTINUITY标记，行号：{disc_lines}")

# 2. 过滤中间广告段（两个DISC之间，4-7个TS）
clean_lines = []
skip_ranges = []

for i in range(len(disc_lines) - 1):
    start = disc_lines[i]
    end = disc_lines[i+1]
    # 统计中间的EXTINF数量
    extinf_count = 0
    for j in range(start + 1, end):
        if lines[j].strip().startswith("#EXTINF:"):
            extinf_count += 1
    # 广告段：EXTINF数量在4-7之间
    if 4 <= extinf_count <= 7:
        skip_ranges.append((start, end))
        log(f"🎯 发现中间广告段：行{start}到行{end}，包含{extinf_count}个TS")

# 3. 过滤掉中间广告
skip = False
current_range = 0
for i, line in enumerate(lines):
    if current_range < len(skip_ranges):
        start, end = skip_ranges[current_range]
        if start <= i <= end:
            skip = True
            if i == end:
                skip = False
                current_range += 1
            continue
    clean_lines.append(line)

log(f"✅ 中间广告删除后行数：{len(clean_lines)}")

# 4. 处理结尾广告（直接在clean_lines里找，不依赖原始行号）
# 从后往前找最后一个DISCONTINUITY
last_disc_idx = -1
endlist_idx = -1
for i in range(len(clean_lines)-1, -1, -1):
    line = clean_lines[i].strip()
    if line == "#EXT-X-DISCONTINUITY":
        last_disc_idx = i
    if line == "#EXT-X-ENDLIST":
        endlist_idx = i
    if last_disc_idx != -1 and endlist_idx != -1:
        break

# 统计DISC到ENDLIST之间的EXTINF数量
if last_disc_idx != -1 and endlist_idx != -1:
    extinf_count = 0
    for j in range(last_disc_idx + 1, endlist_idx):
        if clean_lines[j].strip().startswith("#EXTINF:"):
            extinf_count += 1
    if 4 <= extinf_count <= 7:
        log(f"🎯 发现结尾广告：行{last_disc_idx}到行{endlist_idx}，包含{extinf_count}个TS")
        # 删掉DISC到ENDLIST之间的所有内容，只保留ENDLIST
        clean_lines = clean_lines[:last_disc_idx] + ["#EXT-X-ENDLIST\n"]

# 5. 整理最终内容，去重复ENDLIST
final_content = "".join(clean_lines)
# 确保只有一个ENDLIST
final_content = re.sub(r'#EXT-X-ENDLIST\s*(?=#EXT-X-ENDLIST)', '', final_content)
# 确保格式正确
if not final_content.startswith("#EXTM3U"):
    final_content = "#EXTM3U\n" + final_content
if "#EXT-X-ENDLIST" not in final_content:
    final_content += "#EXT-X-ENDLIST\n"
# 清理多余空行
final_content = re.sub(r'\n+', '\n', final_content).strip() + '\n'

log(f"\n✅ 清理后总行数：{len(final_content.splitlines())}")
log("=== 最终清理结果（最后10行） ===")
log("\n".join(final_content.splitlines()[-10:]))

# 保存文件
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(final_content)

log(f"\n🎉 处理完成！清理结果已保存到 {OUTPUT_FILE}")
