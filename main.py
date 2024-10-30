import os

from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from scraper import get_soup
from option_handlers import handle_rym_list, handle_boomkat, handle_forced_exposure, handle_wfmu_latest, handle_nts_latest, handle_nts_episode, handle_wfmu_list
from utils import options, get_user_selection, album_search, create_playlist, track_search

load_dotenv()

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="playlist-modify-public"
    ))
 
 
testing = False

# testing grounds

if testing == False:
    
    output_type = 'albums'
    selected_option = get_user_selection(options)

    url_input_option = (2,6,8)
    tracks_input_option = (7,8)
    hard_input_option = (3,4,5,6)

    # Text input option
    if selected_option == 1:
        with open(os.getenv("INPUT_PATH"), "r") as file:
            input_list = [tuple(line.strip().split(" - ", 1)) for line in file if line.strip()]
            playlist_name = input("Enter playlist name: ")
            playlist_description = input("Enter playlist description: ")

    # RYM or WFMU list or NTS episode direct input
    if selected_option in url_input_option:
        url = input("Enter URL: ").strip("'\"")

    if selected_option in tracks_input_option:
        output_type = 'tracks'
    
    # Other web scraping options
    if selected_option in hard_input_option:
        url_map = {
            3: "https://boomkat.com/bestsellers?q[release_date]=last-week",
            4: "https://forcedexposure.com/Best/BestIndex.html",
            5: "https://www.wfmu.org/Playlists/Wfmu/",
            6: "https://www.nts.live/latest"
        }
        url = url_map.get(selected_option)
    
    if selected_option != 1:
        soup = get_soup(url)

    if selected_option == 2:
        playlist_name, playlist_description, input_list = handle_rym_list(soup)
    elif selected_option == 3:
        playlist_name, playlist_description, input_list = handle_boomkat(soup)
    elif selected_option == 4:
        playlist_name, playlist_description, input_list = handle_forced_exposure(soup)
    elif selected_option == 5:
        playlist_name, playlist_description, input_list = handle_wfmu_latest(soup)
    elif selected_option == 6:
        playlist_name, playlist_description, input_list = handle_wfmu_list(soup)
    elif selected_option == 7:
        playlist_name, playlist_description, input_list = handle_nts_latest(soup)
    elif selected_option == 8:
        playlist_name, playlist_description, input_list = handle_nts_episode(soup)

    if output_type == 'albums':  
        print("Creating an album-based playlist")
        track_uris, playlist_description, count = album_search(playlist_name, playlist_description, input_list, spotify)
    elif output_type == 'tracks':
        print("Creating a track-based playlist")
        track_uris, playlist_description = track_search(spotify, track_input=input_list, playlist_name=playlist_name, playlist_description=playlist_description)

    create_playlist(track_uris, playlist_description, playlist_name, spotify)
    print(f"Playlist \"{playlist_name}\" has been successfully created!")
    if output_type == 'tracks':
        print(f"It contains {len(track_uris)} tracks!")
    elif output_type == 'albums':
        print(f"It contains {count} albums for a total of {len(track_uris)} tracks!")
    print(f"Get to listening!")