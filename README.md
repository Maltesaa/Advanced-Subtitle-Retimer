# Advanced Subtitle Retimer

**Early hacked together version with little testing. Bugs very possible. Contributions are welcome.**

## Use-case:
You have .mkv files with embedded subtitles and external (.srt or .ass) subtitles that are out of sync. This program will sync them with a very high rate of success. 

Me and most users are probably using this for syncing Japanese subtitles to Anime for the purpose of language learning, therefore you will find some Japanese specific functions in the cleaning part.

## Usage:
Put your .mkv files and your subtitles into the same folder. Then call the script.

You may be prompted about the following:
- Selecting a subtitle stream if multiple exist or the amount of streams don't match. 
- What tags to keep in tagged subtitles. 
- Various operations regarding cleaning up your external subtitles.

After pre-processing is done syncing is performed by calling [alass](https://github.com/kaegi/alass).

## Explanation:
Syncing text subtitles can be tricky due to an abudance of non-dialogue information being present in subtitle files like special effects, karaoke and song lyrics. This script uses some common sense heuristics and the embedded tags to clean those files up before syncing them with alass. So far I've had a 100% success rate with Japanese subtitles.

## Requirements:

- pysubs2 (pip)
- ffprobe
- alass