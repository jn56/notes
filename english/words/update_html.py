import os

# 取得當前腳本所在的目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, 'words.csv')
html_path = os.path.join(script_dir, 'words.html')

print(f"正在讀取 {csv_path}...")
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_content = f.read()
except FileNotFoundError:
    print("找不到 words.csv，請確認檔案是否存在。")
    exit(1)

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
    # 將 CSV 內容插入到兩個標記之間
    new_html = (
        html_content[:start_idx + len(start_marker)] + 
        "\n" + csv_content.strip() + "\n" + 
        html_content[end_idx:]
    )
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print("成功將 words.csv 的資料更新至 words.html 中！")
else:
    print("在 words.html 中找不到對應的標記區塊，更新失敗。")
