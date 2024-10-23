# Text-to-Spotify Playlist Builder

A simple, interactive program that converts input text to a Spotify playlist.

_**Why?**_ When exploring new music I've always preferred listening to albums rather than "top" tracks or algorithmically generated playlists. The problem is that building playlists manually, say from a list like [this](https://rateyourmusic.com/list/funks/the_wires_100_most_important_records_ever_made/), is a lot of copy-paste-searching and click-n-dragging, so I built this to make the process faster and easier.

_The current version is designed for album titles as input._

---

[TOC]

## Getting Started

1. Clone or download a copy of this repo.
2. Install the required dependencies: `pip install python-dotenv spotipy`
3. Rename the included `example.env` to `.env`, change the default input file path if desired, and update with your API credentials.

## Basic Usage

1. Add a list of album titles, each on a new line, to `input.txt`
2. Run the program: `python text-to-spotify-playlist.py`
3. Enter playlist info when prompted.
4. A new playlist will be created from your list!

==_First Authorization:_== The first time you run the program you'll be sent to a Spotify authorization page in your browser. It should be asking you if you want to allow connecting to { _whatever you named your app when getting your API credentails_ }. After this you'll be routed to your Redirect URI. Copy the <u>full</u> URL and paste it into the command prompt to finalize authorization. The OAuth token will be stored in a `.cache` file.

## How It Works

- Reads a text file, parses the info, and creates the relevant Spotify-format search terms. In the current state this means finding the associated URI for each album.
- Uses Spotify OAuth and a user's credentials, safely stored in environment variables, to authenticate with the official Spotify API.
- Prompts user to enter a _name_ and an (optional) _description_ for new playlist creation.
- Iterates through the parsed input info, searches for matches in the Spotify library, and adds them to the newly created playlist.
- Currently, the Spotify API only allows individual tracks or podcast episodes to be added to playlists, not whole albums, so this limitation is circumvented here by...
  - Searching the Spotify library for the album
  - Parsing the match data to find the album URI
  - Using the album URI to fetch the list of tracks from the album
  - Parsing the tracklist data to find each song's URI
  - Adding all of the album's songs, in order, to the new playlist by URI

## How to Get Spotify API Credentials

To get the necessary info for your `.env` file you'll first need a (free) [Spotify Developer](https://developer.spotify.com/) account.

1. After logging in and landing on the dev dashboard click _Create app_.
   ![Screenshot of the Create app screen from the Spotify Developer website](imgs/createapp.JPG){: width="75%"}
2. Fill out the required fields:
   1. Give your app a name (i.e. _Text-to-Playlist App_) and a brief description, maybe something to remind you why you made it.
   2. For the Redirect URI you can supply your own or just use https://example.org/callback. Click _Add_.
   3. Check the box for _Web API_ access and save.
3. After creating the app you'll be taken to its dashboard. Click _Settings_ in the top right corner. Everything you need for your `.env` file is here on this page:
   ![alt text](imgs/appsettings.JPG){: width="75%"}
4. Copy the _Client ID_, click _View client secret_, and if you forgot to copy your Redirect URI earlier you can also see that here. The `example.env` is prepopulated with `https://example.org/callback`.
