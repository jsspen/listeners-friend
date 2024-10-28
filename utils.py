import re
from dotenv import load_dotenv
from datetime import datetime

import spotipy

load_dotenv()

missing = []
album_uris = []
track_uris = []

today_unformatted = datetime.today().date()
today = today_unformatted.strftime('%Y-%m-%d')

options = [
    "Provide a text file",
    "Provide a RateYourMusic list URL",
    "Build from this week's Boomkat Bestsellers list",
    "Build from current Forced Exposure Bestsellers list",
    "Select from WFMU \"Heavy Play\" archive",
    "Provide WFMU \"Heavy Play\" list URL",
    "Browse latest NTS episodes",
    "Provide an NTS episode URL"
]

def display_options(options):
    # Check if this is just a bunch of strings to print or something more complex
    if type(options[0]) == str:
        for idx, option in enumerate(options, start=1):
            print(f"{idx}. {option}")
    # Right now this is just for displaying lists of NTS Episodes
    else:
        for idx, option in enumerate(options, start=1):
            tags = " #".join(f"{option['tags'][i]}" for i in range(len(option["tags"])))
            print(f"{idx}. {option['date']} {option['title']}, {option['location']} #{tags}")
        
def get_user_selection(options):
    while True:
        display_options(options)
        try:
            selected_option = int(input("Please select an option: "))
            if 1 <= selected_option <= len(options):
                return selected_option
            else:
                print(f"Invalid selection. Please choose a number between 1 and {len(options)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Print number of missing items to file and prepend basic info to playlist description
def handle_missing(missing, playlist_name, playlist_description):
    clean_playlist_name = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", playlist_name)
    with open(f"not_found_for_{clean_playlist_name}_{today}.txt", "w", encoding="utf-8") as file:
            file.write("Not Found:\n")
            for item in missing:
                file.write(item + "\n")
    playlist_description = str(len(missing)) + " items not found. " + playlist_description
    return playlist_description

def album_search(playlist_name, playlist_description, input_list, spotify):
    # Search for each album
    for artist, album in input_list:
        # album specific search using Spotify's "album:{query}" format
        # returns only the top result
        result = spotify.search(q='album:' + album + ' artist:' + artist, type="album", limit=1)
        if result['albums']['items']:
            album_uris.append(result['albums']['items'][0]['uri'])
        else:
            missing.append(artist + " - " + album)

    if len(missing) > 0:
        playlist_description = handle_missing(missing, playlist_name, playlist_description)
        
    track_uris = track_search(spotify, album_uris)
    return track_uris, playlist_description, (len(input_list) - len(missing))

# Take album URIs and return track URIs
def track_search(spotify, album_uris = None, track_input = None, playlist_name = None, playlist_description = None):
    if album_uris:
        # Get the tracks for each album URI
        for album in album_uris:
            tracks = spotify.album_tracks(album)['items']
            # Get the URIs for each track
            for track in tracks:
                track_uris.append(track['uri'])
        return track_uris
    elif track_input:
        for track in track_input:
            artist, title = track
            result = spotify.search(q=f"artist:{artist} track:{title}", type="track", limit=1)
            if result['tracks']['items']:
                uri = result['tracks']['items'][0]['uri']
                if uri:
                    track_uris.append(uri)
            else:
                missing.append(artist + " - " + title)
        if len(missing) > 0:
            playlist_description = handle_missing(missing, playlist_name, playlist_description)
        return track_uris, playlist_description

# Break potentially huge list of tracks into easily manageable chunks
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Take track URIs and final playlist title & description
def create_playlist(track_uris, playlist_description, playlist_name, spotify):
    # Create the new playlist
    user_id = spotify.current_user()["id"]
    playlist = spotify.user_playlist_create(user_id, playlist_name, public=True, description=playlist_description)
    track_uris = [uri for uri in track_uris if uri is not None]

    # Split to chunks of 100 tracks, the max allowed by the API in a single post
    for chunk in chunk_list(track_uris, 100):
        try:
            spotify.playlist_add_items(playlist['id'], chunk)
        except spotipy.exceptions.SpotifyException as e:
            print(f"An error occurred: {e}")