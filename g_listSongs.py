import random
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sites = 'https://www.ultimate-guitar.com'

# Open the file, read lines, and shuffle the list randomly
with open('g_files/bandsToDo.txt', 'r') as fd:
    lines = fd.readlines()

random.shuffle(lines)  # Shuffle the lines list

for line in lines:
    print("Processing:", line.strip())
    if "https" not in line:
        continue

    site = line.strip()
    hdr = {
        'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                       '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    print('Fetching site:', site)
    req = Request(site, headers=hdr)
    try:
        page = urlopen(req)
    except HTTPError as e:
        print("HTTPError:", e.read())
        continue  # Skip to the next site on error

    # Read the entire HTML page once.
    html = page.read()
    print("Page fetched successfully.")

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Look for the <div> element containing our JSON data.
    store_div = soup.find("div", class_="js-store")
    if not store_div:
        print("Could not find the JSON data store.")
        continue

    data_content = store_div.get("data-content")
    if not data_content:
        print("No data-content attribute found on js-store div.")
        continue

    try:
        # Parse the JSON content
        data_json = json.loads(data_content)
    except Exception as ex:
        print("Error parsing JSON:", ex)
        continue

    # Navigate the JSON object to where the tabs data is stored.
    # In this example, we are assuming that the tab data is in:
    # data_json -> "store" -> "page" -> "data" -> "other_tabs"
    # (You may need to adjust this if the site structure changes or if you want to check
    # other sections like "top_tabs", "latest_tabs", or "album_tabs")
    page_data = data_json.get("store", {}).get("page", {}).get("data", {})
    other_tabs = page_data.get("other_tabs", [])
    if not other_tabs:
        print("No 'other_tabs' found in the JSON data.")
        continue

    # Process each tab entry and extract the "tab_url"
    for tab in other_tabs:
        tab_url = tab.get("tab_url")
        if tab_url:
            print("Found tab_url:", tab_url)
            with open('g_files/songsToDo.txt', 'a') as h:
                h.write(tab_url + '\n')
        else:
            print("No tab_url in this tab entry.")

    # Optionally, you may also check other sections
    # For example, to look through "top_tabs" or "latest_tabs", you could add:
    #
    # for key in ["top_tabs", "latest_tabs", "album_tabs"]:
    #     tabs_list = page_data.get(key, [])
    #     for tab in tabs_list:
    #         tab_url = tab.get("tab_url")
    #         if tab_url:
    #             print("Found tab_url in {}: {}".format(key, tab_url))
    #             with open('g_files/songsToDo.txt', 'a') as h:
    #                 h.write(tab_url + '\n')
