import os
import time
import json
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from urllib.parse import urlparse

# Ensure the output directory exists.
output_dir = "data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def safe_filename(text):
    """
    Create a safe filename from text.
    Allow alphanumeric characters and underscores.
    """
    return "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in text).replace(" ", "_")

# Open the file containing the list of URLs.
with open('g_files/songsToDo.txt', 'r') as fd:
    for site in fd:
        site = site.strip()
        if not site:
            continue

        # Parse URL and attempt to derive artist and song slugs from the path.
        parsed_url = urlparse(site)
        path_parts = parsed_url.path.split('/')
        # Expecting a URL like: /tab/godley-and-creme/a-little-piece-of-heaven-chords-1453987
        if len(path_parts) >= 4:
            artist_slug = safe_filename(path_parts[2])
            song_slug = safe_filename(path_parts[3])
        else:
            artist_slug = "unknown_artist"
            song_slug = "unknown_song"
        
        # Build the output filename.
        filename = os.path.join(output_dir, f"db_{artist_slug}_{song_slug}.txt")
        
        # Skip this URL if file already exists.
        if os.path.exists(filename):
            print(f"File '{filename}' already exists. Skipping {site}.")
            # Even when skipping, wait the delay if you desire uniform pacing.
            time.sleep(4)
            continue

        # Set up headers to mimic a browser.
        hdr = {
            'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                           '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        req = urllib.request.Request(site, headers=hdr)

        try:
            page = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(f"HTTP error for {site}: {e.read()}")
            time.sleep(4)
            continue

        page_content = page.read()
        soup = BeautifulSoup(page_content, "html.parser")

        # Find the <div> that holds the JSON data (look for 'js-store')
        div_store = soup.find("div", class_="js-store")
        if not div_store:
            print(f"js-store div not found on {site}")
            time.sleep(4)
            continue

        data_json = div_store.get("data-content")
        if not data_json:
            print(f"No data-content attribute found on {site}")
            time.sleep(4)
            continue

        try:
            data = json.loads(data_json)
        except Exception as e:
            print(f"Error parsing JSON from {site}: {e}")
            time.sleep(4)
            continue

        # Extract tab content and metadata from the JSON.
        try:
            tab_content = data["store"]["page"]["data"]["tab_view"]["wiki_tab"]["content"]
            tab_info = data["store"]["page"]["data"]["tab"]
            artist_name = tab_info["artist_name"]
            song_name = tab_info["song_name"]
            # Genre (using "chord_type" in the parent data; might be empty)
            genre = data["store"]["page"]["data"].get("chord_type", "")
            # Musical key from "tonality_name" if provided.
            key_val = tab_info.get("tonality_name", "")
        except Exception as e:
            print(f"Error extracting data from JSON on {site}: {e}")
            time.sleep(4)
            continue

        # Create a header with URL, artist, song, genre, and key.
        header = (f"URL: {site}\n"
                  f"Artist: {artist_name}\n"
                  f"Song: {song_name}\n"
                  f"Genre: {genre}\n"
                  f"Key: {key_val}\n\n\n")
        full_text = header + tab_content

        # Write the header and tab to the file.
        try:
            with open(filename, "w", encoding="utf-8") as out_file:
                out_file.write(full_text)
            print(f"Saved tab for '{song_name}' by '{artist_name}' to '{filename}'")
        except Exception as e:
            print(f"Error writing file {filename}: {e}")

        # Delay for ~4 seconds between requests.
        time.sleep(4)
