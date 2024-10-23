import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load .env variables
load_dotenv()

# Initialize arrays for holding URIs
album_uris = []
track_uris = []

# Set up auth
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-modify-public"
))

# Read input file lines into an array
with open(os.getenv("INPUT_PATH"), "r") as file:
    inputList = [line.strip() for line in file if line.strip()]

# Prompt user for playlist name and description
playlist_name = input("Enter playlist name: ")
playlist_description = input("Enter playlist description: ")

# Search for the each line from the file
for album in inputList:
    # album specific search using Spotify's "album:{query}" format
    # returns only the top result
    result = spotify.search(q='album:' + album, type='album', limit=1)
    if result['albums']['items']:
        # Add the album URI to the array
        album_uris.append(result['albums']['items'][0]['uri'])
# Get the tracks for each album_uri in the array
for album in album_uris:
    tracks = spotify.album_tracks(album)['items']
    # Get the URIs for each track
    for track in tracks:
        # Add the track URI to the array
        track_uris.append(track['uri'])
        
# Create the new playlist and add the tracks
user_id = spotify.current_user()["id"]
playlist = spotify.user_playlist_create(user_id, playlist_name, public=True, description=playlist_description)
spotify.playlist_add_items(playlist['id'], track_uris)
