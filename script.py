from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import hashlib
import re
from pathlib import Path

#  Link limits
main_limit = 300
others_limit = 200

#  Main and other Telegram channels
main_channel = "https://t.me/s/ConfigsHubPlus"
other_channels = [
    "https://t.me/s/vpnfreak",
    "https://t.me/s/mypremium98",
    "https://t.me/s/Glysit",
    "https://t.me/s/Here_is_Nowhere",
    "https://t.me/s/sinavm",
    "https://t.me/s/prrofile_purple",
    "https://t.me/s/mitivpn"
]


output_folder = Path("output")
output_folder.mkdir(exist_ok=True)

# 📃 Track seen hashes to avoid duplicates
seen_file = output_folder / "seen_hashes.txt"
if seen_file.exists():
    with open(seen_file, "w", encoding="utf-8") as f:
        seen_hashes = set(line.strip() for line in f if line.strip())
else:
    seen_hashes = set()

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

protocol_regex = r"(?:vless|vmess|trojan|ss|ssr|tuic|hysteria)://[^\s]+"


def scrape_channel(channel_url, max_links):
    driver.get(channel_url)
    time.sleep(5)
    scroll_count = 0
    max_scrolls = 100
    collected_links = []

    while len(collected_links) < max_links and scroll_count < max_scrolls:
        messages = driver.find_elements(By.CLASS_NAME, "tgme_widget_message_text")
        for msg in messages:
            content = msg.text.strip()
            for link in re.findall(protocol_regex, content, flags=re.IGNORECASE):
                protocol = link.split("://")[0].lower()
                hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()

                if hash_digest not in seen_hashes:
                    seen_hashes.add(hash_digest)
                    collected_links.append((protocol, link))
                    if len(collected_links) >= max_links:
                        break

 
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_count += 1

    return collected_links


main_links = scrape_channel(main_channel, main_limit)


other_links = []
for channel in other_channels:
    if len(other_links) >= others_limit:
        break
    remaining = others_limit - len(other_links)
    new_links = scrape_channel(channel, remaining)
    other_links.extend(new_links)


driver.quit()
all_links = main_links + other_links
print(f" Total collected: {len(all_links)} links")

if all_links:
    all_txt_path = output_folder / "all.txt"
    with open(all_txt_path, "a", encoding="utf-8") as f:
        for _, link in all_links:
            f.write(link + "\n")


    per_protocol = {}
    for proto, link in all_links:
        per_protocol.setdefault(proto, []).append(link)

    for proto, links in per_protocol.items():
        proto_path = output_folder / f"{proto}.txt"
        with open(proto_path, "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")


    with open(seen_file, "a", encoding="utf-8") as f:
        for _, link in all_links:
            hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()
            f.write(hash_digest + "\n")

    print(f" Saved {len(main_links)} from main + {len(other_links)} from others.")
else:
    print(" No new config links found.")
