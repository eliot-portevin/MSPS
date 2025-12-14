# Music Streaming Platform Synchronisation

## Overview

This project aims to synchronise playlists and liked tracks between different music streaming services, focusing
primarily on services like YouTube Music and Spotify.
The goal is to create a seamless experience for users who want to
switch between platforms while retaining their favorite music content.

In addition to this, users are given the option to download tracks directly to their local machine for offline
listening.
This is achieved by leveraging the [youtube-dl](https://github.com/ytdl-org/youtube-dl) library to download
tracks from YouTube Music.

The program is written in Python and comes in the form of a command-line
interface ([simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu)).
Users can navigate through the menu to
select desired actions using arrow keys or vim-like keybindings (j, k).
Multi-selection is supported by pressing the
SpaceBar or [Tab] to select/deselect items.
Users can then press [Enter] to confirm their selection.

## Features

- **Platform Support:** Currently supports synchronization between YouTube Music and Spotify.
- **Playlist Transfer:** Seamlessly transfer playlists between supported platforms.
- **Fuzzy Matching:** Utilize fuzzy string matching to handle variations in track information and avoid duplicates.

## Dependencies

### Python Libraries (install via `pip install -r requirements.txt`):

- [ytmusicapi](https://github.com/sigma67/ytmusicapi): Python library for interacting with the YouTube Music API.
- [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy): Python library for fuzzy string matching.
- [spotipy](https://github.com/spotipy-dev/spotipy): Python library for interacting with the Spotify API.
- [simple-term-menu](https://github.com/IngoMeyer441/simple-term-menu): Python library for creating command-line
  interfaces.

### Other Tools:

- [youtube-dl](https://github.com/ytdl-org/youtube-dl): Download tracks from YouTube Music. **Note:** Requires python
  3.10 or higher.
- [ffmpeg](https://ffmpeg.org/): Convert downloaded tracks to mp3 format and embed metadata.

## Getting Started

1. Install dependencies (see above).
2. Configure API keys for the desired music streaming services:
   - **YouTube Music** (*Authentication to YouTube Music is compulsory since this is where all tracks are downloaded from*)
       Unfortunately, automated authentication has stopped working for the **ytmusicapi** module. Thus, manual browser authentication is now necessary. To do so, follow these [steps](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html):
       - Open a Firefox browser tab (it isn't guaranteed that other browsers will work).
       - Open a [YouTube Music](https://music.youtube.com/) tab and make sure that you are logged in. Close the YouTube Music tab.
       - Open the developer tools pane, and navigate to the **Network** tab.
       - Open a YouTube Music tab, and look at the requests in the developer pane. Pick any of the requests, so long as it contains the following details: `Status` 200, `Method` POST, `Domain` youtube.music.com, and so on.
       - Right-click on the request and select *Copy Request Headers*.
       - Open a terminal window, and navigate to the **MSPS** directory. On Windows, insert the following command:
           - `ytmusicapi browser [paste request headers] --file config/auth_ytmusic.json`
       - On Mac, only 1024 can be pasted to std input. Thus, the request headers have to be piped to the **ytmusicapi** command as such:
           - `pbpaste | ytmusicapi browser --file config/auth_ytmusic.json`
     - **Spotify**
      Follow the instructions [here](https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app) to register your app and obtain a client ID and client secret. You will be asked to enter these when running the script for the first time (if either your source or destination platform is Spotify).
3. Run the script: `python main.py`

## Future Tasks

The project is a work in progress, and future tasks include:

- **Expand Platform Support:** Extend synchronization support to additional music streaming services.
- **Enhance Fuzzy Matching:** Fine-tune fuzzy matching algorithms for improved accuracy.
- **Playlist Cleanup:** Implement a cleanup function to remove existing duplicate tracks from playlists.
- **Error Handling:** Implement robust error handling to gracefully manage exceptions.

## Contribution

Contributions and suggestions are welcome! Feel free to open issues or pull requests.
