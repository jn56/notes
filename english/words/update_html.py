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

tags_keywords = {
    'Tech': ['程式', '電腦', '系統', '資料', '網路', '技術', '科技', '研發', '機器', '人工智慧', '晶片', '裝置', '軟體', '硬體', '伺服器', '雲端', '安全', 'AI', '架構', '網路安全', '虛擬', '數位', '自動化', '演算法'],
    'Economy': ['經濟', '商業', '企業', '投資', '貸款', '財務', '銀行', '貨幣', '資金', '市場', '交易', '成本', '費用', '收益', '獲利', '薪水', '購買', '銷售', '公司', '股票', '利息', '資產', '商務', '產業', '行銷'],
    'Global': ['國際', '國家', '政府', '政治', '戰爭', '軍事', '外交', '法律', '全球', '協議', '條約', '組織', '社會', '選舉', '政策', '條款', '管轄', '司法', '權利', '義務', '世界', '跨國'],
}

def assign_tags(row):
    text_to_check = row[0] + ' ' + row[1] + ' ' + row[2] + ' ' + row[3]
    assigned = []
    for tag, keywords in tags_keywords.items():
        if any(kw in text_to_check for kw in keywords):
            assigned.append(tag)
    
    if not assigned:
        assigned.append('Life')
    
    return ','.join(assigned[:2])

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'words.csv')
html_path = os.path.join(script_dir, 'words.html')

print(f"正在讀取並處理 {csv_path}（自動取得音標與分類標籤）...")
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) < 5:
            header.append('音標')
        if len(header) < 6:
            header.append('標籤')
        rows = list(reader)
except FileNotFoundError:
    print("找不到 words.csv，請確認檔案是否存在。")
    exit(1)

def process_row(row):
    # Ensure row has 6 columns
    while len(row) < 6:
        row.append('')
        
    # Get IPA if missing
    if not row[4].strip():
        row[4] = get_ipa(row[0])
        
    # Assign tags if missing
    if not row[5].strip():
        row[5] = assign_tags(row)
        
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
    print("成功將資料、音標與標籤更新至 words.html 中！")
else:
    print("在 words.html 中找不到對應的標記區塊，更新失敗。")
