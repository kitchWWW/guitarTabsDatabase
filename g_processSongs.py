import os
import time
import random
import json
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from urllib.parse import urlparse

# Adjustable sleep time between requests (in seconds)
SLEEP_TIME = 0.2

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

def extract_filename_from_url(site):
    """
    Extract a candidate filename from the URL.
    For example, if the URL is:
      https://tabs.ultimate-guitar.com/tab/h-e-a-t/point-of-no-return-tabs-1800875
    this returns something like "h_e_a_t_point_of_no_return_tabs_1800875"
    """
    parsed = urlparse(site)
    # Remove leading/trailing slashes from the path.
    path = parsed.path.strip('/')
    parts = path.split('/')
    # If the URL follows the expected pattern (e.g., "tab/artist/songName-..."),
    # join the parts beyond the first one.
    if len(parts) >= 3 and parts[0] == "tab":
        file_tag = "_".join(parts[1:])
    else:
        file_tag = site
    return safe_filename(file_tag)

# Open the file containing the list of URLs.
with open('g_files/songsToDo.txt', 'r') as fd:
    allLines = fd.readlines()
    random.shuffle(allLines)
    for site in allLines:
        site = site.strip()
        if not site:
            print("skipping "+site)
            continue

        if("guitar-pro" in site):
            print("skipping "+site)
            #they parse different
            continue
        if("/pro/" in site):
            print("skipping "+site)
            #they parse different
            continue
        if("-official-" in site):
            print("skipping "+site)
            #they parse different
            continue

        # Infer the filename early using the URL structure.
        file_tag = extract_filename_from_url(site)
        filename = os.path.join(output_dir, f"db_{file_tag}.txt")
        
        # Check if file already exists before doing the request.
        if os.path.exists(filename):
            print(f"File '{filename}' already exists. Skipping {site}.")
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
        print("requesting "+site)
        req = urllib.request.Request(site, headers=hdr)
        # Fetch the URL.
        try:
            page = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print(f"HTTP error for {site}: {e.read()}")
            time.sleep(SLEEP_TIME)
            print("\a")
            continue
        print("got it")

        page_content = page.read()
        soup = BeautifulSoup(page_content, "html.parser")

        # Locate the <div> with class 'js-store'.
        div_store = soup.find("div", class_="js-store")
        if not div_store:
            print(f"js-store div not found on {site}")
            time.sleep(SLEEP_TIME)
            continue

        data_json = div_store.get("data-content")
        if not data_json:
            print(f"No data-content attribute found on {site}")
            time.sleep(SLEEP_TIME)
            continue

        try:
            data = json.loads(data_json)
        except Exception as e:
            print(f"Error parsing JSON from {site}: {e}")
            time.sleep(SLEEP_TIME)
            continue

        # Extract tab content and metadata.
        try:
            tab_content = data["store"]["page"]["data"]["tab_view"]["wiki_tab"]["content"]
            tab_info = data["store"]["page"]["data"]["tab"]
            artist_name = tab_info.get("artist_name")
            song_name = tab_info.get("song_name")
            genre = data["store"]["page"]["data"].get("chord_type", "")
            key_val = tab_info.get("tonality_name", "")
        except Exception as e:
            print(f"Error extracting data from JSON on {site}: {e}")
            time.sleep(SLEEP_TIME)
            continue

        # If valid artist and song names are available, update the filename.
        if (artist_name and song_name and 
            artist_name.lower() not in ["unknown", "unknown_artist"] and 
            song_name.lower() not in ["unknown", "unknown_song"]):
            new_file_tag = f"{safe_filename(artist_name)}_{safe_filename(song_name)}"
            filename_new = os.path.join(output_dir, f"db_{new_file_tag}.txt")
            if os.path.exists(filename_new):
                print(f"File '{filename_new}' already exists. Skipping {site}.")
                time.sleep(SLEEP_TIME)
                continue
            else:
                # Use the more specific filename.
                file_tag = new_file_tag
                filename = filename_new

        # Create a header with metadata.
        header = (
            f"URL: {site}\n"
            f"Artist: {artist_name if artist_name else 'N/A'}\n"
            f"Song: {song_name if song_name else 'N/A'}\n"
            f"Genre: {genre}\n"
            f"Key: {key_val}\n\n\n"
        )
        full_text = header + tab_content

        # Write the header and tab content to the file.
        try:
            with open(filename, "w", encoding="utf-8") as out_file:
                out_file.write(full_text)
            print(f"Saved tab for '{song_name}' by '{artist_name}' to '{filename}'")
        except Exception as e:
            print(f"Error writing file {filename}: {e}")

        # Delay between requests.
        time.sleep(SLEEP_TIME)
