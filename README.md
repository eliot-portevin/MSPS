# YT-Music-Down
A simple python script to automate the download of one's liked songs from YouTube Music.
Uses [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/) to connect to google and
retrieve the songs and [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download the songs once
their ids have been obtained.

## Dependencies
### ytmusicapi
See [the docs](https://ytmusicapi.readthedocs.io/en/stable/index.html) for installation and
usage instructions. TLDR: `pip install ytmusicapi`.

### yt-dlp
Specific instructions for installation can be found 
[here](https://github.com/yt-dlp/yt-dlp#installation). In our case, `pip install yt-dlp` suffices.

### ffmpeg
This is required by yt-dlp to merge the audio and video streams. Installation instructions can be
found [here](https://ffmpeg.org/download.html).
#### Linux
You're probably capable of figuring out whether your package manager has ffmpeg or not. If not,
you can always build from [source](https://github.com/FFmpeg/FFmpeg).
#### Windows
Download the latest build from [here](https://ffmpeg.org/download.html#build-windows). Extract the
zip file and add the `bin` folder to your PATH.
#### MacOS
Install via [homebrew](https://brew.sh/): `brew install ffmpeg`.

## Usage
Run `python main.py` and follow the prompts. If it's your first time running the script, you will
be prompted to log in to your google account. To do so, click on the link provided and follow the
Google instructions. Once this is done, go back to the terminal and press **Enter**. You will then
be asked how many songs you wish to download. Keep in mind that ytmusicapi can only access musics in
chunks, entering "18" may therefore very well lead to 20 or 50 songs being downloaded. Once you have
entered a valid number *n*, the script will proceed to download your *n* most recently liked songs to
a `Downloads` folder in the same directory as the script. If some songs are already present in the
said folder, they will be skipped.