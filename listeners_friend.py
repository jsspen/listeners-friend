import os
import re
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()

today_unformatted = datetime.today().date()
today = today_unformatted.strftime('%Y-%m-%d')
input_list = []
album_uris = []
track_uris = []
missing = []

# authorization
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

if selected_option == '1':
    with open(os.getenv("INPUT_PATH"), "r") as file:
        input_list = [tuple(line.strip().split(" - ", 1)) for line in file if line.strip()]
        playlist_name = input("Enter playlist name: ")
        playlist_description = input("Enter playlist description: ")

# If using scraped data instead of text input
if selected_option != '1':
    if selected_option == '2':
        url = input("Enter list URL: ")
    if selected_option == '3':
        url = "https://boomkat.com/bestsellers?q[release_date]=last-week"
    if selected_option == '4':
        url = "https://forcedexposure.com/Best/BestIndex.html"
    if selected_option == '5':
        url = "https://www.wfmu.org/Playlists/Wfmu/"
    
    
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    driver.quit()
    
    # Using a RYM list as input
    if selected_option == '2':
        playlist_name = soup.find('h1').get_text(strip=True)
        playlist_description = soup.find('span', class_='rendered_text').get_text(strip=True)
        # Truncate long descriptions to fit within Spotify's 300 character limit
        # Also taking into consideration the 20-22 chars of "### albums not found. " prepended later
        playlist_description = (playlist_description[:275] + '...') if len(playlist_description) > 278 else playlist_description
        list = soup.find('table', id='user_list')
        if list is None:
            print("not found")
        else: 
            for row in list.find_all('tr'):
                # Find artist, album title, and year
                artist_tag = row.find('a', class_='list_artist')
                album_tag = row.find('a', class_='list_album')
                if not artist_tag or not album_tag:
                    continue
                artist = artist_tag.get_text(strip=True)
                album = album_tag.get_text(strip=True)
                input_list.append((artist, album))
    
    # Using the Boomkat list as input
    if selected_option == '3':
        bestsellers_list = soup.find('div', class_='bestsellers').find('ol', class_='bestsellers-list')
        if bestsellers_list is None:
            print("not found")
        else: 
            for item in bestsellers_list.find_all('li', class_='bestsellers-item'):
                artist = item.find('div', class_='product-name').find_all('a')[0].text.strip()
                album = item.find('div', class_='product-name').find_all('a')[1].text.strip()
                input_list.append((artist, album))
        playlist_name = "This Week's Boomkat Bestsellers"
        playlist_description = "For the week ending " + today
        
    # Using the ForcedExposure list as input
    if selected_option == '4':
        playlist_name = "Forced Exposure Bestsellers"
        playlist_description = "As of " + today
        bestsellers_list = soup.find('table', id='ctl00_ContentPlaceHolder1_gvRecBestSeller')
        for row in bestsellers_list.find_all('tr', class_='search_resultfields'):
            artist_tag = row.find('a', id=lambda x: x and 'hlnkArtistId' in x)
            artist_name = artist_tag.text.strip() if artist_tag else None
            album_tag = row.find('a', id=lambda x: x and 'hrTitle' in x)
            album_title = album_tag.text.strip() if album_tag else None
            if artist_name and album_title:
                input_list.append((artist_name, album_title))

    # using WFMU
    if selected_option == '5':
        year = input("For what year (1987-present): ")
        print("Select a date: ")
        for a_tag in soup.find_all("a", class_="playlist"):
            href = a_tag.get("href")
            match = re.search(r"/(\d{4})/", href)
            if match:
                url_year = match.group(1)
                if url_year == year:
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2})\.html", href)
                    if date_match:
                        date = date_match.group(1)
                        print(date)
        date = input("Enter selection as YYYY-MM-DD: ")
        
        sub_url = "http://blogfiles.wfmu.org/BT/Airplay_Lists/" + year + "/" + date + ".html"
        match = re.search(r"(\d{4}-\d{2}-\d{2})", sub_url)
        
        driver = webdriver.Chrome()
        driver.get(sub_url)
        html = driver.page_source
        second_bowl_of_soup = BeautifulSoup(html, 'html.parser')

        driver.quit()
        
        date = match.group(1)
        playlist_name = "WFMU Heavy Play " + date
        playlist_description = ""
        for ul in second_bowl_of_soup.find_all('ul'):
            if any(li.find('strong') for li in ul.find_all('li')):
                for li in ul.find_all('li'):
                    match = re.match(r'^(.*?) - (.*?) \((.*?)\)$', li.text)
                    if match:
                        artist_name, album_title, record_label = match.groups()
                        input_list.append((artist_name, album_title))


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

# Break potentially huge list of tracks into easily manageable chunks
def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

# Split to chunks of 100 tracks, the max allowed by the API in a single post
for chunk in chunk_list(track_uris, 100):
    try:
        spotify.playlist_add_items(playlist['id'], chunk)
    except spotipy.exceptions.SpotifyException as e:
        print(f"An error occurred: {e}")
