import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()

today_unformatted = datetime.today().date()
today = today_unformatted.strftime('%Y-%m-%d')
album_uris = []
track_uris = []

# authorization
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-modify-public"
))

boomkat = input("Grab this week's Boomkat bestseller list (y/n)? ")
if boomkat == 'y':
    url = "https://boomkat.com/bestsellers?q[release_date]=last-week"
    
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    driver.quit()
    
    bestsellers_list = soup.find('div', class_='bestsellers').find('ol', class_='bestsellers-list')
    if bestsellers_list is None:
        print("not found")
    else: 
        inputList = []
        for item in bestsellers_list.find_all('li', class_='bestsellers-item'):
            artist = item.find('div', class_='product-name').find_all('a')[0].text.strip()
            album = item.find('div', class_='product-name').find_all('a')[1].text.strip()
            inputList.append((artist, album))
    
else:
    with open(os.getenv("INPUT_PATH"), "r") as file:
        inputList = [line.strip() for line in file if line.strip()]

if boomkat == 'y':
    playlist_name = "Boomkat Bestsellers: Week Ending " + today
    playlist_description = ''
else:
    playlist_name = input("Enter playlist name: ")
    playlist_description = input("Enter playlist description: ")

missing = []

# Search for each album
for artist, album in inputList:
    # album specific search using Spotify's "album:{query}" format
    # returns only the top result
    result = spotify.search(q='album:' + album, type='album', limit=1)
    if result['albums']['items']:
        album_uris.append(result['albums']['items'][0]['uri'])
    else:
        missing.append(artist + " - " + album)

# Print missing album info to console & save to text file
# If making a Boomkat Bestseller playlist add number of missing albums to the description
with open("not_found.txt", "w", encoding="utf-8") as file:
    file.write("Not Found:\n")
    print("Not Found:")
    for album in missing:
        print(album)
        file.write(album + "\n")
# Update playlist description with number of albums not found.
playlist_description = str(len(missing)) + " albums not found. " + playlist_description

# Get the tracks for each album URI
for album in album_uris:
    tracks = spotify.album_tracks(album)['items']
    # Get the URIs for each track
    for track in tracks:
        track_uris.append(track['uri'])

# Create the new playlist
user_id = spotify.current_user()["id"]
playlist = spotify.user_playlist_create(user_id, playlist_name, public=True, description=playlist_description)
track_uris = [uri for uri in track_uris if uri is not None]

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Break list into chunks of 100 due to limitations of the Spotify API
for chunk in chunk_list(track_uris, 100):
    try:
        spotify.playlist_add_items(playlist['id'], chunk)
    except spotipy.exceptions.SpotifyException as e:
        print(f"An error occurred: {e}")
