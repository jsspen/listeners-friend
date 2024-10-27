import os
from dotenv import load_dotenv
from datetime import datetime

import spotipy


load_dotenv()

missing = []
album_uris = []
track_uris = []

today_unformatted = datetime.today().date()
today = today_unformatted.strftime('%Y-%m-%d')

# Needs playlist_name for titling the missing file
# Needs playlist_description to update chosen/generated description with missing info
# Needs input_list to process
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

    # Print missing album info to console & save to text file
    # Add number of missing albums to the description
    if len(missing) > 0:
        with open(f"not_found_for_{playlist_name}_{today}.txt", "w", encoding="utf-8") as file:
            file.write("Not Found:\n")
            # print("Not Found:")
            for album in missing:
                # print(album)
                file.write(album + "\n")
        # Update playlist description with number of albums not found.
        playlist_description = str(len(missing)) + " albums not found. " + playlist_description
        
    track_uris = track_search(album_uris, spotify)
    # returns track_uris to send to the playlist creator
    # returns playlist description as its been updated with missing number
    # playlist_name only read, not changed
    return track_uris, playlist_description

# Take album URIs and return track URIs
def track_search(album_uris, spotify):
    # Get the tracks for each album URI
    for album in album_uris:
        tracks = spotify.album_tracks(album)['items']
        # Get the URIs for each track
        for track in tracks:
            track_uris.append(track['uri'])
    return track_uris

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