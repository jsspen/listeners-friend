import os

from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from scraper import get_soup
from option_handlers import handle_option_2, handle_option_3, handle_option_4, handle_option_5
from utils import album_search, create_playlist

load_dotenv()

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="playlist-modify-public"
    ))

print("1. Use a text file")
print("2. Use a RateYourMusic List")
print("3. Use this week's Boomkat Bestseller List")
print("4. Use current ForcedExposure Bestseller List")
print("5. Select WFMU Heavy Play List")
selected_option = input("Please select an option: ")

# Text input option
if selected_option == '1':
    with open(os.getenv("INPUT_PATH"), "r") as file:
        input_list = [tuple(line.strip().split(" - ", 1)) for line in file if line.strip()]
        playlist_name = input("Enter playlist name: ")
        playlist_description = input("Enter playlist description: ")
        
# RYM list input option
if selected_option == '2':
    url = input("Enter list URL: ")
    
else:
    url_map = {
        '3': "https://boomkat.com/bestsellers?q[release_date]=last-week",
        '4': "https://forcedexposure.com/Best/BestIndex.html",
        '5': "https://www.wfmu.org/Playlists/Wfmu/"
    }
    url = url_map.get(selected_option)
    
if not url:
    print("Invalid option selected.")
else:
    soup = get_soup(url)
    if selected_option == '2':
        playlist_name, playlist_description, input_list = handle_option_2(soup)
    elif selected_option == '3':
        playlist_name, playlist_description, input_list = handle_option_3(soup)
    elif selected_option == '4':
        playlist_name, playlist_description, input_list = handle_option_4(soup)
    elif selected_option == '5':
        playlist_name, playlist_description, input_list = handle_option_5(soup)
    
    track_uris, playlist_description = album_search(playlist_name, playlist_description, input_list, spotify)
    create_playlist(track_uris, playlist_description, playlist_name, spotify)
