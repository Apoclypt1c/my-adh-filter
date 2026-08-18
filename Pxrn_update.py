import urllib.request
import os
from datetime import datetime, timezone, timedelta

BASE_FILE = 'PXRN-Base.list'
OUTPUT_FILE = 'PXRN-filter.list'
V2FLY_URL = 'https://raw.githubusercontent.com/v2fly/domain-list-community/refs/heads/master/data/category-porn'

rules = set()

# 1. 读取并解析本地基础文件 PXRN-Base.list
if os.path.exists(BASE_FILE):
    with open(BASE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                rule_type = parts[0].lower()
                domain = parts[1].lower()
                if rule_type in ['host', 'host-suffix', 'host-keyword']:
                    rules.add((rule_type, domain))

# 2. 抓取并解析 v2fly 规则
try:
    req = urllib.request.Request(V2FLY_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 过滤属性标记（如 @cn）
            if '@' in line:
                line = line.split('@')[0].strip()
            
            # 规则映射转换
            if line.startswith('full:'):
                rules.add(('host', line[5:].strip().lower()))
            elif line.startswith('keyword:'):
                rules.add(('host-keyword', line[8:].strip().lower()))
            elif line.startswith('regexp:') or line.startswith('include:'):
                continue
            else:
                rules.add(('host-suffix', line.strip().lower()))
except Exception as e:
    print(f"Fetch remote list error: {e}")

# 3. 排序与规则分类统计
sorted_rules = sorted(list(rules), key=lambda x: (x[0], x[1]))

host_count = sum(1 for r in sorted_rules if r[0] == 'host')
suffix_count = sum(1 for r in sorted_rules if r[0] == 'host-suffix')
keyword_count = sum(1 for r in sorted_rules if r[0] == 'host-keyword')
total_count = len(sorted_rules)

# 计算北京时间 (UTC+8)
bj_time = datetime.now(timezone.utc) + timedelta(hours=8)
time_str = bj_time.strftime('%Y-%m-%d %H:%M:%S UTC+8')

# 4. 写入文件（头部增加状态注释）
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(f"# Updated: {time_str}\n")
    f.write(f"# Total: {total_count} (host: {host_count}, host-suffix: {suffix_count}, host-keyword: {keyword_count})\n")
    f.write(f"# Remote Source: {V2FLY_URL}\n")
    f.write("#\n")
    for rule_type, domain in sorted_rules:
        f.write(f"{rule_type}, {domain}\n")

print(f"Updated {OUTPUT_FILE} with {total_count} rules.")
