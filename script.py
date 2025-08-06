from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import hashlib
import re
from pathlib import Path

#  Link collection limits
main_limit = 700
others_limit = 200

#  Telegram channels
main_channel = "https://t.me/s/ConfigsHubPlus"
other_channels = [
    "https://t.me/s/vpnfreak",
    "https://t.me/s/mypremium98",
    "https://t.me/s/Glysit",
    "https://t.me/s/Here_is_Nowhere",
    "https://t.me/s/sinavm",
    "https://t.me/s/prrofile_purple",
    "https://t.me/s/mitivpn",
    "https://t.me/s/v2ray_free_conf",
    "https://t.me/s/BigSmoke_Config",
    "https://t.me/s/IP_CF_Config",
    "https://t.me/s/vless_config",
    "https://t.me/s/Airdorap_Free",
    "https://t.me/s/FREECONFIGSPLUS",
    "https://t.me/s/connect_vpnz",
    "https://t.me/s/unlocked_worlld",
    "https://t.me/s/frog_v2ray",
    "https://t.me/s/khosrow_vpn",
    "https://t.me/s/thefreedomvpn",
    "https://t.me/s/manisecure_vpn",
    "https://t.me/s/v2rayng_ghavi",
    "https://t.me/s/v2ray_hub1",
    "https://t.me/s/mahsa_net",
    "https://t.me/s/config2rayfree34",
    "https://t.me/s/azadnet",
    "https://t.me/s/godot404",
    "https://t.me/s/v2sayfree",
    "https://t.me/s/vpnjey",
    "https://t.me/s/lx3vpn",
    "https://t.me/s/iran.i",
    "https://t.me/s/ispeedtopvpn",
    'https://t.me/s/MARAMBASHI',
]

#  Setup output folder
output_folder = Path("output")
output_folder.mkdir(exist_ok=True)

#  Load previously seen hashes (to avoid duplicates)
seen_file = output_folder / "seen_hashes.txt"
seen_hashes = set()
if seen_file.exists():
    with open(seen_file, "r", encoding="utf-8") as f:
        seen_hashes = set(line.strip() for line in f if line.strip())

#  Chrome WebDriver setup
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#  Regex pattern for config links
protocol_regex = r"(?:vless|vmess|trojan|ss|ssr|tuic|hysteria)://[^\s]+"


def scrape_channel(channel_url, max_links):
    driver.get(channel_url)
    time.sleep(0.1)
    scroll_count = 0
    max_scrolls = 300
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

        # Scroll to bottom to load more
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)
        scroll_count += 1

    return collected_links


#  Scrape main and other channels
main_links = scrape_channel(main_channel, main_limit)

other_links = []
for channel in other_channels:
    if len(other_links) >= others_limit:
        break
    remaining = others_limit - len(other_links)
    other_links.extend(scrape_channel(channel, remaining))

driver.quit()

#  Combine and report
all_links = main_links + other_links
print(f" Total collected: {len(all_links)} links")

#  Save results
if all_links:
    # Save all links
    all_txt_path = output_folder / "all_Saber_ConfigsHub-V2Ray.txt"
    with open(all_txt_path, "w", encoding="utf-8") as f:
        for _, link in all_links:
            f.write(link + "\n")

    # Save by protocol
    per_protocol = {}
    for proto, link in all_links:
        per_protocol.setdefault(proto, []).append(link)

    for proto, links in per_protocol.items():
        proto_path = output_folder / f"{proto}_Saber_ConfigsHub-V2Ray.txt"
        with open(proto_path, "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")

    # Save seen hashes
    with open(seen_file, "a", encoding="utf-8") as f:
        for _, link in all_links:
            hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()
            f.write(hash_digest + "\n")

    print(f" Saved {len(main_links)} from main + {len(other_links)} from others.")
else:
    print(" No new config links found.")
