import json
import glob
import re
import numpy as np
import statistics

# Precompiled regular expressions.
MAJOR_PATTERN = re.compile(r'^[A-G](#|b)?(maj)?$', flags=re.IGNORECASE)
MINOR_PATTERN = re.compile(r'^[A-G](#|b)?m$', flags=re.IGNORECASE)

def is_chromatic(chord):
    """
    Returns True if a chord is considered chromatic.
    
    A chord is non-chromatic (returns False) if:
      - It is an inversion (contains a slash, e.g. "C#m/E")
      - It is a plain major chord (e.g. "C", "F", "Amaj")
      - It is a plain minor chord (e.g. "Am", "C#m")
    
    Otherwise, returns True (it has alterations such as 7, add9, etc.).
    """
    chord = chord.strip()
    if MAJOR_PATTERN.match(chord):
        return False
    if MINOR_PATTERN.match(chord):
        return False
    return True

def compute_chromaticness(chords):
    """
    Given a list of chords, computes the ratio of unique chords that are chromatic.
    Returns a float between 0 and 1.
    """
    unique = set(chords)
    if not unique:
        return 0.0
    chromatic_count = sum(1 for chord in unique if is_chromatic(chord))
    return chromatic_count / len(unique)

def compute_summary_stats(data):
    """
    Given a list of numbers, computes a dictionary with:
      - average ("avg")
      - mode ("mode") – in case of multiple modes, uses the smallest value
      - minimum ("min")
      - maximum ("max")
      - first quartile ("q1")
      - third quartile ("q3")
    If data is empty, returns None for each stat.
    """
    if not data:
        return {"avg": None, "mode": None, "min": None, "max": None, "q1": None, "q3": None}
    avg = sum(data) / len(data)
    try:
        mode_val = statistics.mode(data)
    except statistics.StatisticsError:
        mode_val = min(statistics.multimode(data))
    mn = min(data)
    mx = max(data)
    q1 = float(np.percentile(data, 25))
    q3 = float(np.percentile(data, 75))
    return {"avg": avg, "mode": mode_val, "min": mn, "max": mx, "q1": q1, "q3": q3}

def analyze_songs_detailed(song_files):
    """
    Process a list of JSON song files and compute detailed summary stats.
    
    Only songs with at least one non-empty verse and one non-empty chorus are kept.
    For each section type (verses, choruses, bridges, pre-choruses, intros, outros),
    and for each song (across all sections), we record:
      - Total chord count,
      - Unique chord count,
      - Chromaticness (ratio of unique chords that have chromatic alterations).
    
    Additionally, we record per song counts of the number of verses, choruses, bridges,
    pre-choruses, intros, and outros. For verses and choruses (present in every song
    by definition), we also compute the number of shared unique chords.
    
    For every metric (for example, chords per verse) we then compute summary statistics:
        average, mode, min, max, Q1, and Q3.
    
    Returns a dictionary of summary stats.
    """
    # These dictionaries will hold per-instance metric values.
    metrics = {
        "verse": {"chords": [], "unique": [], "chromatic": []},
        "chorus": {"chords": [], "unique": [], "chromatic": []},
        "bridge": {"chords": [], "unique": [], "chromatic": []},
        "prechorus": {"chords": [], "unique": [], "chromatic": []},
        "intro": {"chords": [], "unique": [], "chromatic": []},
        "outro": {"chords": [], "unique": [], "chromatic": []}
    }
    
    # Song-level metrics.
    song_metrics = {"chords": [], "unique": [], "chromatic": [], "shared": []}
    # Song-level counts for section instances.
    song_counts = {
        "verses": [],
        "choruses": [],
        "bridges": [],
        "prechoruses": [],
        "intros": [],
        "outros": []
    }
    
    songs_kept = []
    # Load JSON files and filter out those that lack at least one non-empty verse and chorus.
    for filepath in song_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue
        
        verses = {k: v for k, v in data.items() if k.lower().startswith("verse") and v}
        choruses = {k: v for k, v in data.items() if k.lower().startswith("chorus") and v}
        if verses and choruses:
            songs_kept.append(data)
    
    if not songs_kept:
        print("No songs with at least one non-empty verse and one non-empty chorus were found.")
        return {}
    
    # Process each valid song.
    for song in songs_kept:
        # Filter sections by type (only non-empty ones).
        verses = {k: v for k, v in song.items() if k.lower().startswith("verse") and v}
        choruses = {k: v for k, v in song.items() if k.lower().startswith("chorus") and v}
        bridges = {k: v for k, v in song.items() if k.lower().startswith("bridge") and v}
        pre_choruses = {k: v for k, v in song.items() if k.lower().startswith("pre-chorus") and v}
        intros = {k: v for k, v in song.items() if k.lower().startswith("intro") and v}
        outros = {k: v for k, v in song.items() if k.lower().startswith("outro") and v}
        
        # Record song-level counts.
        song_counts["verses"].append(len(verses))
        song_counts["choruses"].append(len(choruses))
        song_counts["bridges"].append(len(bridges))
        song_counts["prechoruses"].append(len(pre_choruses))
        song_counts["intros"].append(len(intros))
        song_counts["outros"].append(len(outros))
        
        # Process each instance in verses.
        for chords in verses.values():
            metrics["verse"]["chords"].append(len(chords))
            metrics["verse"]["unique"].append(len(set(chords)))
            metrics["verse"]["chromatic"].append(compute_chromaticness(chords))
        
        # Process each instance in choruses.
        for chords in choruses.values():
            metrics["chorus"]["chords"].append(len(chords))
            metrics["chorus"]["unique"].append(len(set(chords)))
            metrics["chorus"]["chromatic"].append(compute_chromaticness(chords))
        
        # Process bridges.
        for chords in bridges.values():
            metrics["bridge"]["chords"].append(len(chords))
            metrics["bridge"]["unique"].append(len(set(chords)))
            metrics["bridge"]["chromatic"].append(compute_chromaticness(chords))
        
        # Process pre-choruses.
        for chords in pre_choruses.values():
            metrics["prechorus"]["chords"].append(len(chords))
            metrics["prechorus"]["unique"].append(len(set(chords)))
            metrics["prechorus"]["chromatic"].append(compute_chromaticness(chords))
        
        # Process intros.
        for chords in intros.values():
            metrics["intro"]["chords"].append(len(chords))
            metrics["intro"]["unique"].append(len(set(chords)))
            metrics["intro"]["chromatic"].append(compute_chromaticness(chords))
        
        # Process outros.
        for chords in outros.values():
            metrics["outro"]["chords"].append(len(chords))
            metrics["outro"]["unique"].append(len(set(chords)))
            metrics["outro"]["chromatic"].append(compute_chromaticness(chords))
        
        # Compute song-level data (considering all sections).
        song_all_chords = []
        for section in [verses, choruses, bridges, pre_choruses, intros, outros]:
            for chords in section.values():
                song_all_chords.extend(chords)
        song_total_chords = sum(len(chords) for section in [verses, choruses, bridges, pre_choruses, intros, outros] 
                                 for chords in section.values())
        song_unique = len(set(song_all_chords))
        song_chromatic = compute_chromaticness(song_all_chords)
        song_metrics["chords"].append(song_total_chords)
        song_metrics["unique"].append(song_unique)
        song_metrics["chromatic"].append(song_chromatic)
        
        # Compute shared unique chords between verses and choruses.
        verse_unique = set()
        for chords in verses.values():
            verse_unique.update(chords)
        chorus_unique = set()
        for chords in choruses.values():
            chorus_unique.update(chords)
        shared = len(verse_unique.intersection(chorus_unique))
        song_metrics["shared"].append(shared)
    
    # Now, compile summary stats for every metric.
    results = {
        "verse": {
            "chords": compute_summary_stats(metrics["verse"]["chords"]),
            "unique": compute_summary_stats(metrics["verse"]["unique"]),
            "chromatic": compute_summary_stats(metrics["verse"]["chromatic"]),
        },
        "chorus": {
            "chords": compute_summary_stats(metrics["chorus"]["chords"]),
            "unique": compute_summary_stats(metrics["chorus"]["unique"]),
            "chromatic": compute_summary_stats(metrics["chorus"]["chromatic"]),
        },
        "bridge": {
            "chords": compute_summary_stats(metrics["bridge"]["chords"]),
            "unique": compute_summary_stats(metrics["bridge"]["unique"]),
            "chromatic": compute_summary_stats(metrics["bridge"]["chromatic"]),
        },
        "prechorus": {
            "chords": compute_summary_stats(metrics["prechorus"]["chords"]),
            "unique": compute_summary_stats(metrics["prechorus"]["unique"]),
            "chromatic": compute_summary_stats(metrics["prechorus"]["chromatic"]),
        },
        "intro": {
            "chords": compute_summary_stats(metrics["intro"]["chords"]),
            "unique": compute_summary_stats(metrics["intro"]["unique"]),
            "chromatic": compute_summary_stats(metrics["intro"]["chromatic"]),
        },
        "outro": {
            "chords": compute_summary_stats(metrics["outro"]["chords"]),
            "unique": compute_summary_stats(metrics["outro"]["unique"]),
            "chromatic": compute_summary_stats(metrics["outro"]["chromatic"]),
        },
        "song": {
            "chords": compute_summary_stats(song_metrics["chords"]),
            "unique": compute_summary_stats(song_metrics["unique"]),
            "chromatic": compute_summary_stats(song_metrics["chromatic"]),
            "shared": compute_summary_stats(song_metrics["shared"])
        },
        "song_counts": {
            "verses": compute_summary_stats(song_counts["verses"]),
            "choruses": compute_summary_stats(song_counts["choruses"]),
            "bridges": compute_summary_stats(song_counts["bridges"]),
            "prechoruses": compute_summary_stats(song_counts["prechoruses"]),
            "intros": compute_summary_stats(song_counts["intros"]),
            "outros": compute_summary_stats(song_counts["outros"])
        },
        "total_songs": len(songs_kept)
    }
    
    return results

# Example usage:
if __name__ == "__main__":
    song_files = glob.glob("out_structure_and_chords/*.txt")
    detailed_stats = analyze_songs_detailed(song_files)
    
    if detailed_stats:
        import pprint
        pprint.pprint(detailed_stats)
