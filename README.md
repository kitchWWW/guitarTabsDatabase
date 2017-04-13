# Popular Music Chord Database

A tool that generates a database of chords used in popular music. Pulls from www.ultimate-guitar.com

The result is a text file in which each line is an entry of the form

```
<url> \t [chord1, chord2, chord3, ... ]
```

## Dependencies 

* beautifulsoup4
* some standard python libraries

## Me talking for a bit

Welcome! the interesting part you are probably here for is in g_files/database.txt. That is where we have a stash of all the chords in all the songs we could get our hands on.