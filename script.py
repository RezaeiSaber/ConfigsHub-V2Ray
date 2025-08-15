from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import hashlib
import re
from pathlib import Path

# Limits
main_limit = 900
others_limit = 50
max_per_file = 1200

# Channels
main_channel = "https://t.me/s/ConfigsHUB"
other_channels = [
    "https://t.me/s/vpnfreak",
    "https://t.me/s/mypremium98",
    "https://t.me/s/Glysit",
    "https://t.me/s/Here_is_Nowhere",
    "https://t.me/s/sinavm",
    "https://t.me/s/prrofile_purple",
    "https://t.me/s/mitivpn",
    "https://t.me/s/v2ray_free_conf",
]

# Output folder
output_folder = Path("output")
output_folder.mkdir(exist_ok=True)

# Seen hashes
seen_file = output_folder / "seen_hashes.txt"
seen_hashes = set()
if seen_file.exists():
    with open(seen_file, "r", encoding="utf-8") as f:
        seen_hashes = set(line.strip() for line in f if line.strip())

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-images")
options.add_argument("--disable-javascript")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

protocol_regex = r"(?:vless|vmess|trojan|ss|ssr|tuic|hysteria)://[^\s]+"

def scrape_channel(channel_url, max_links):
    driver.get(channel_url)
    time.sleep(1)
    scroll_count = 0
    max_scrolls = 200
    collected_links = []
    processed_messages = set()
    
    print(f"Scraping {channel_url}...")

    while len(collected_links) < max_links and scroll_count < max_scrolls:
        messages = driver.find_elements(By.CLASS_NAME, "tgme_widget_message_text")
        new_messages_found = False
        
        for msg in messages:
       
            msg_id = msg.get_attribute('outerHTML')[:200]
            
            if msg_id in processed_messages:
                continue
                
            processed_messages.add(msg_id)
            new_messages_found = True
            
            content = msg.text.strip()
            if not content:
                continue
                
        
            links = re.findall(protocol_regex, content, flags=re.IGNORECASE)
            
            for link in links:
            
                hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()

                if hash_digest not in seen_hashes:
                    protocol = link.split("://")[0].lower()
                    seen_hashes.add(hash_digest)
                    collected_links.append((protocol, link))
                    
                    if len(collected_links) >= max_links:
                        print(f"Reached limit of {max_links} links")
                        return collected_links


        if not new_messages_found and scroll_count > 5:
            print("No new messages found, stopping...")
            break


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        scroll_count += 1
        
        if scroll_count % 10 == 0:
            print(f"Scroll {scroll_count}, found {len(collected_links)} links")

    print(f"Finished scraping {channel_url}: {len(collected_links)} links found")
    return collected_links

def trim_file(file_path, max_lines):
 
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if len(lines) > max_lines:
            lines = lines[-max_lines:]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

# Scrape
print("Starting to scrape channels...")
print(f"Target: {main_limit} from main channel, {others_limit} total from {len(other_channels)} other channels")

start_time = time.time()
main_links = scrape_channel(main_channel, main_limit)
main_time = time.time() - start_time
print(f"Main channel completed in {main_time:.1f} seconds")

other_links = []
for i, channel in enumerate(other_channels, 1):
    if len(other_links) >= others_limit:
        break
    remaining = others_limit - len(other_links)
    print(f"\nScraping channel {i}/{len(other_channels)}: {channel}")
    channel_start = time.time()
    channel_links = scrape_channel(channel, remaining)
    channel_time = time.time() - channel_start
    print(f"Channel {i} completed in {channel_time:.1f} seconds, found {len(channel_links)} links")
    other_links.extend(channel_links)

driver.quit()
total_time = time.time() - start_time
print(f"\nTotal scraping completed in {total_time:.1f} seconds")

all_links = main_links + other_links
print(f" Total collected: {len(all_links)} links")

if all_links:
    # Save all links
    all_txt_path = output_folder / "all_Saber_ConfigsHub-V2Ray.txt"
    with open(all_txt_path, "a", encoding="utf-8") as f:
        for _, link in all_links:
            f.write(link + "\n")
    trim_file(all_txt_path, max_per_file)

    # Save by protocol
    per_protocol = {}
    for proto, link in all_links:
        per_protocol.setdefault(proto, []).append(link)

    for proto, links in per_protocol.items():
        proto_path = output_folder / f"{proto}_Saber_ConfigsHub-V2Ray.txt"
        with open(proto_path, "a", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        trim_file(proto_path, max_per_file)

    # Save seen hashes
    with open(seen_file, "a", encoding="utf-8") as f:
        for _, link in all_links:
            hash_digest = hashlib.sha256(link.encode("utf-8")).hexdigest()
            f.write(hash_digest + "\n")

    print(f" Saved {len(main_links)} from main + {len(other_links)} from others.")
else:
    print(" No new config links found.")
