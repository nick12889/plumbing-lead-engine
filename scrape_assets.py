import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Load clients data
with open('Clients.json', 'r') as f:
    clients = json.load(f)

os.makedirs('./logos', exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for client in clients:
    slug = client['slug']
    website = client.get('website')
    logo_filename = f"{slug}.png"
    local_logo_path = f"./logos/{logo_filename}"
    downloaded = False

    # 1. Try direct download from logo_url
    if client.get('logo_url'):
        try:
            res = requests.get(client['logo_url'], headers=headers, timeout=10)
            if res.status_code == 200 and len(res.content) > 500:
                with open(local_logo_path, 'wb') as img_f:
                    img_f.write(res.content)
                downloaded = True
        except Exception:
            pass

    # 2. Fallback scrape from website
    if website and not downloaded:
        try:
            res = requests.get(website, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                img_tag = soup.find('img', src=re.compile(r'logo', re.I)) or soup.find('img')
                if img_tag and img_tag.get('src'):
                    full_logo_url = urljoin(website, img_tag['src'])
                    img_res = requests.get(full_logo_url, headers=headers, timeout=10)
                    if img_res.status_code == 200:
                        with open(local_logo_path, 'wb') as img_f:
                            img_f.write(img_res.content)
                        downloaded = True
        except Exception:
            pass

    # Update relative path for web fetching
    client['local_logo_url'] = f"./logos/{logo_filename}" if downloaded else ""

# Save updated JSON
with open('Clients.json', 'w') as f:
    json.dump(clients, f, indent=2)
