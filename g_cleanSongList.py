import urllib.parse

def is_valid_url(url: str) -> bool:
    """
    Check if the provided URL is syntactically valid.
    
    Uses urllib.parse.urlparse to break down the URL and verifies that:
      - The scheme is either 'http' or 'https'
      - The network location (netloc) is non-empty
    """
    parsed = urllib.parse.urlparse(url)
    # Checking that the URL scheme is http(s) and that there's a network location
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

def clean_url_file(input_path: str, output_path: str) -> None:
    """
    Reads a text file with URLs, removes duplicates and lines with invalid URLs,
    and writes the valid, unique URLs to a new file.
    
    :param input_path: Path to the input file containing URLs.
    :param output_path: Path to the output file to write cleaned URLs.
    """
    unique_urls = set()
    valid_urls = []

    # Open the input file and process each line.
    with open(input_path, 'r') as infile:
        for line in infile:
            # Remove surrounding whitespace and newline characters.
            url = line.strip()
            
            # Check if the URL is already processed and if it passes the valid URL check.
            if url and url not in unique_urls and is_valid_url(url):
                unique_urls.add(url)
                valid_urls.append(url)

    # Write the valid, unique URLs to the output file.
    with open(output_path, 'w') as outfile:
        for url in valid_urls:
            outfile.write(url + '\n')

if __name__ == '__main__':
    # Define the paths for the input and output files.
    input_file = 'g_files/songsToDo.txt'
    output_file = 'g_files/clean_songsToDo.txt'
    clean_url_file(input_file, output_file)
    print(f"Cleaned file has been saved to {output_file}")
