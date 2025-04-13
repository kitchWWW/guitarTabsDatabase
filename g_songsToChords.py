import os
import re
import json

def parse_file(content):
    """
    Parses the file content to detect song sections (e.g. intro, verse, chorus, etc.)
    and extracts chords contained in the [ch]...[/ch] markers.

    Returns:
        A dictionary where keys are the section names (if only one occurrence) or 
        "sectionname-<counter>" for multiple sections, and the values are arrays of chords.
    """
    # Updated regex pattern for section headers:
    # It matches headers which:
    # - Either start at the beginning of a line with optional whitespace OR are inside brackets '[...]'
    # - Then capture one of the section names (intro, verse, chorus, bridge, pre-chorus, solo, outro, coro, pre-coro) ignoring case.
    # - Optionally, there can be an accompanying number (e.g., "Verse 1") and then either a closing bracket or punctuation.
    header_pattern = re.compile(
        r'(?i)(?:^\s*|\[)\s*(?P<section>intro|verse|chorus|bridge|pre-chorus|instrumental|solo|outro|coro|pre-coro)(?:\s*(?P<number>\d+))?\s*(?:\]|\:|\-|\.\s+)',
        re.MULTILINE
    )
    
    # Find all section header matches along with their positions
    matches = list(header_pattern.finditer(content))
    
    if not matches:
        # If no section headers are found, you may opt to return an empty dict,
        # or store all chords under a default section like "unknown"
        return {}
    
    # A mapping to translate Spanish section names to English
    translation = {
        'coro': 'chorus',
        'pre-coro': 'pre-chorus'
    }
    
    # Use a dictionary to hold each section's occurrences;
    # each key's value is a list of lists (chord lists) for each occurrence.
    sections_dict = {}
    
    for i, match in enumerate(matches):
        # Extract section name, normalizing to lower case
        section = match.group('section').lower()
        # Translate Spanish labels to English if necessary
        section = translation.get(section, section)
        
        # If a number is provided (e.g., "Verse 1"), it could be used to further distinguish occurrences.
        # Here, we ignore it in the key naming since we will add numeric suffixes for multiple occurrences.
        start = match.end()  # Start of the content after the header
        
        # End is either the start of the next header or the end of file
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end]
        
        # Find all chords in the section using [ch]...[/ch]
        chords = re.findall(r'\[ch\](.+?)\[/ch\]', section_content, flags=re.IGNORECASE)
        chords = [ch.strip() for ch in chords]  # Clean up chord strings
        
        if section not in sections_dict:
            sections_dict[section] = []
        sections_dict[section].append(chords)
    
    # Format final dictionary: for sections that occur once, use the section name directly.
    # For multiple occurrences, suffix with a counter (e.g. "verse-1", "verse-2").
    result = {}
    for section, chord_lists in sections_dict.items():
        if len(chord_lists) == 1:
            result[section] = chord_lists[0]
        else:
            for i, chords in enumerate(chord_lists, start=1):
                key = f"{section}-{i}"
                result[key] = chords
                
    return result

def process_files(input_dir, output_dir):
    """
    Walks through every .txt file in input_dir, processes them to extract
    the song structure and chords, and writes out JSON files to output_dir
    with the same filename.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_filepath = os.path.join(input_dir, filename)
            with open(input_filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            parsed_structure = parse_file(content)
            output_filepath = os.path.join(output_dir, filename)
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(parsed_structure, f, indent=4)
            print(f"Processed '{filename}' and saved to '{output_filepath}'.")

if __name__ == "__main__":
    input_directory = "data"
    output_directory = "out_structure_and_chords"
    process_files(input_directory, output_directory)
