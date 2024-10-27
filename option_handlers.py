from datetime import datetime
import re
from scraper import get_soup

today_unformatted = datetime.today().date()
today = today_unformatted.strftime('%Y-%m-%d')
input_list = []

# RYM List
def handle_option_2(soup):
    playlist_name = soup.find('h1').get_text(strip=True)
    playlist_description = soup.find('span', class_='rendered_text').get_text(strip=True)
    if playlist_description is None:
        playlist_description = ''
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
    return playlist_name, playlist_description, input_list

# Boomkat Bestsellers List
def handle_option_3(soup):
    table = soup.find('div', class_='bestsellers')
    if table is None:
        print("table not found")
    bestsellers_list = table.find('ol', class_='bestsellers-list')
    if bestsellers_list is None:
        print("bestsellers list not found")
        print(table)
    else: 
        for item in bestsellers_list.find_all('li', class_='bestsellers-item'):
            artist = item.find('div', class_='product-name').find_all('a')[0].text.strip().title()
            album = item.find('div', class_='product-name').find_all('a')[1].text.strip()
            input_list.append((artist, album))
    playlist_name = "This Week's Boomkat Bestsellers"
    playlist_description = "For the week ending " + today
    return playlist_name, playlist_description, input_list

# Forced Exposure Bestsellers List    
def handle_option_4(soup):
    playlist_name = "Forced Exposure Bestsellers"
    playlist_description = "As of " + today
    bestsellers_list = soup.find('table', id='ctl00_ContentPlaceHolder1_gvRecBestSeller')
    for row in bestsellers_list.find_all('tr', class_='search_resultfields'):
        artist_tag = row.find('a', id=lambda x: x and 'hlnkArtistId' in x)
        artist_name = artist_tag.text.strip().title() if artist_tag else None
        album_tag = row.find('a', id=lambda x: x and 'hrTitle' in x)
        album_title = album_tag.text.strip() if album_tag else None
        if artist_name and album_title:
            input_list.append((artist_name, album_title))
    return playlist_name, playlist_description, input_list

# WFMU Heavy Rotation Playlists            
def handle_option_5(soup):
    
    # Make a selection from the available playlists
    year = input("For what year (1987-present): ")
    print("Select a date: ")
    
    # List available dates for selected year as YYYY-MM-DD
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
    second_bowl_of_soup = get_soup(sub_url)
    match = re.search(r"(\d{4}-\d{2}-\d{2})", sub_url)
    date = match.group(1)
    playlist_name = "WFMU Heavy Play " + date
    playlist_description = ""
    for ul in second_bowl_of_soup.find_all('ul'):
        if any(li.find('strong') for li in ul.find_all('li')):
            for li in ul.find_all('li'):
                match = re.match(r'^(.*?) - (.*?) \((.*?)\)$', li.text)
                if match:
                    artist_name, album_title, record_label = match.groups()
                    input_list.append((artist_name.title(), album_title))
    return playlist_name, playlist_description, input_list