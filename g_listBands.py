import json
from bs4 import BeautifulSoup
import urllib.request
import urllib.error

# Loop through letters D through Z.
for letter in [chr(x) for x in range(ord('j'), ord('z') + 1)]:
    print(f"\nProcessing letter: {letter.upper()}")
    
    # Flag to determine whether to skip the current letter.
    skip_to_next_letter = False
    
    # Base URL for the current letter, e.g., for letter "d":
    # https://www.ultimate-guitar.com/bands/d1.htm, https://www.ultimate-guitar.com/bands/d2.htm, etc.
    site_base = "https://www.ultimate-guitar.com/bands/" + letter
    page = 1
    page_count = 200

    while True:
        url = site_base + str(page) + ".htm"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                          '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            response = urllib.request.urlopen(req)
            html = response.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"HTTP 404 Error encountered on page {page} for letter {letter} - skipping to next letter.")
                skip_to_next_letter = True
                break  # Exit inner loop for current letter.
            else:
                print("HTTP Error on page", page)
                print(e.read().decode("utf-8"))
                skip_to_next_letter = True
                break

        print("Processing page:", url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the div that contains our JSON data.
        store_div = soup.find("div", class_="js-store")
        if store_div is None:
            print(f"No 'js-store' div found on page {page} for letter {letter} - skipping to next letter.")
            skip_to_next_letter = True
            break

        data_content = store_div.get("data-content")
        if not data_content:
            print(f"No data-content found on page {page} for letter {letter} - skipping to next letter.")
            skip_to_next_letter = True
            break

        try:
            data_json = json.loads(data_content)
        except Exception as ex:
            print(f"Error parsing JSON on page {page} for letter {letter}: {ex}")
            skip_to_next_letter = True
            break

        # Try to locate the band information inside the JSON.
        try:
            # The structure is assumed to be: data_json["store"]["page"]["data"]["artists"]
            artists = data_json["store"]["page"]["data"]["artists"]
        except KeyError:
            print(f"No artists found in JSON on page {page} for letter {letter}")
            skip_to_next_letter = True
            break

        # If no artists exist on this page, then we're done with this letter.
        if not artists:
            print(f"No artists to process on page {page} for letter {letter}")
            break

        # Process each band/artist.
        for artist in artists:
            # The JSON provides a relative URL (e.g., "/artist/a_2385").
            # Prepend the base URL.
            full_link = "https://www.ultimate-guitar.com" + artist["artist_url"]
            print(full_link)
            with open("g_files/bandsToDo.txt", "a", encoding="utf-8") as fd:
                fd.write(full_link + "\n")

        if page >= page_count:
            print(f"Reached the last page for letter {letter}: {page_count}")
            break

        page += 1

    # Check whether we need to skip to the next letter.
    if skip_to_next_letter:
        continue  # This is optional since break in the inner loop will naturally lead to the next iteration of the outer loop.
