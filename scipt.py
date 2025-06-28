from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import hashlib
import re
from pathlib import Path

# 📍 Telegram channel link
channel_url = "https://t.me/s/ConfigsHubPlus"

# 📁 Folder structure setup
configs_folder = Path("C:/Users/Saber/Documents/GitHub/ConfigsHub-V2Ray")
configs_folder.mkdir(parents=True, exist_ok=True)

# 📃 Tracking hashes to avoid duplicates
seen_file = configs_folder / "seen_hashes.txt"
if seen_file.exists():
    with open(seen_file, "r", encoding="utf-8") as f:
        seen_hashes = set(line.strip() for line in f if line.strip())
else:
    seen_hashes = set()

# 🌐 Selenium setup (headless)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get(channel_url)
time.sleep(5)

# 🧠 Regex for extracting full config links (without capturing group)
proto_regex = r"(?:vless|vmess|trojan|ss|ssr|tuic|hysteria)://[^\s]+"

# ⚙️ Parameters
max_links_to_find = 100
max_scrolls = 50

# 🧾 Data structures
found_links = {
    "vmess": [],
    "vless": [],
    "trojan": [],
    "ss": [],
    "ssr": [],
    "tuic": [],
    "hysteria": [],
    "other": [],
}
all_new_links = []
scrolls = 0

while len(all_new_links) < max_links_to_find and scrolls < max_scrolls:
    messages = driver.find_elements(By.CLASS_NAME, "tgme_widget_message_text")
    for msg in messages:
        content = msg.text.strip()
  
        for link in re.findall(proto_regex, content, flags=re.IGNORECASE):
            proto = link.split("://")[0].lower()
            hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()
            if hash_digest not in seen_hashes:
                all_new_links.append(link)
                seen_hashes.add(hash_digest)
                found_links.get(proto, found_links["other"]).append(link)
                if len(all_new_links) >= max_links_to_find:
                    break
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    scrolls += 1

driver.quit()

# ✅ Save section (append to fixed files)
if all_new_links:
    # 🗂 Save all configs to all.txt
    all_path = configs_folder / "all.txt"
    with open(all_path, "a", encoding="utf-8") as f:
        for link in all_new_links:
            f.write(link + "\n")

    # 📂 Save per protocol files
    for proto, links in found_links.items():
        if not links:
            continue
        proto_path = configs_folder / f"{proto}.txt"
        with open(proto_path, "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")

    # 🔐 Update seen hashes file
    with open(seen_file, "a", encoding="utf-8") as f:
        for link in all_new_links:
            hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()
            f.write(hash_digest + "\n")

    print(f"✅ Added {len(all_new_links)} new config links (from last {max_links_to_find} posts).")
else:
    print("⚠️ No new configs found.")
