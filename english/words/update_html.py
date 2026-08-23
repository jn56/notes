import os
import csv
import urllib.request
import urllib.parse
import json
import concurrent.futures

def get_ipa(word):
    clean = word.split('/')[0].strip()
    clean = clean.replace('[', '').replace(']', '')
    try:
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + urllib.parse.quote(clean)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            ipa = data[0].get('phonetic', '')
            if not ipa:
                for p in data[0].get('phonetics', []):
                    if 'text' in p and p['text']:
                        ipa = p['text']
                        break
            return ipa
    except Exception:
        return ''

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'words.csv')
html_path = os.path.join(script_dir, 'words.html')

print(f"正在讀取並處理 {csv_path}（若有新單字將自動取得音標）...")
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) < 5:
            header.append('音標')
        rows = list(reader)
except FileNotFoundError:
    print("找不到 words.csv，請確認檔案是否存在。")
    exit(1)

def process_row(row):
    if len(row) >= 5 and row[4].strip():
        return row
    word = row[0]
    ipa = get_ipa(word)
    if len(row) >= 5:
        row[4] = ipa
    else:
        row.append(ipa)
    return row

# 使用多執行緒加速音標查詢
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    updated_rows = list(executor.map(process_row, rows))

# 寫回 words.csv
with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(updated_rows)

# 讀取更新後的 csv 內容為字串
with open(csv_path, 'r', encoding='utf-8') as f:
    csv_content = f.read()

print(f"正在更新 {html_path}...")
try:
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
except FileNotFoundError:
    print("找不到 words.html，請確認檔案是否存在。")
    exit(1)

start_marker = "/*CSV_START*/"
end_marker = "/*CSV_END*/"

start_idx = html_content.find(start_marker)
end_idx = html_content.find(end_marker)

if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
    new_html = (
        html_content[:start_idx + len(start_marker)] + 
        "\n" + csv_content.strip() + "\n" + 
        html_content[end_idx:]
    )
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("成功將資料與音標更新至 words.html 中！")
else:
    print("在 words.html 中找不到對應的標記區塊，更新失敗。")
