from datetime import datetime
import re
from scraper import get_soup
from utils import get_user_selection

today_unformatted = datetime.today().date()
today = today_unformatted.strftime('%Y-%m-%d')
input_list = []

# RYM List
def handle_rym_list(soup):
    playlist_name = soup.find('h1').get_text(strip=True)
    playlist_description = soup.find('span', class_='rendered_text')
    if playlist_description is None:
        playlist_description = ''
    else:
        playlist_description = playlist_description.get_text(strip=True)
    # Truncate long descriptions to fit within Spotify's 300 character limit
    # Also taking into consideration the 19-21 chars of "### items not found. " prepended later
    playlist_description = (playlist_description[:276] + '...') if len(playlist_description) > 279 else playlist_description
    
    has_next_page = False
    next_url = None
    
    nav_div = soup.find('div', id='nav_bottom')
    if nav_div:
        nav_span = nav_div.find('span', class_='navspan')
        if nav_span:
            navlink_next = nav_span.find('a', class_='navlinknext')
            if navlink_next:
                next_url = navlink_next['href']
                if next_url:
                    next_url = "https://rateyourmusic.com" + next_url
                    has_next_page = True
        
    list = soup.find('table', id='user_list')
    if list is None:
        print("List not found")
    else: 
        for row in list.find_all('tr'):
            artist_tag = row.find('a', class_='list_artist')
            album_tag = row.find('a', class_='list_album')
            if not artist_tag or not album_tag:
                continue
            artist = artist_tag.get_text(strip=True)
            album = album_tag.get_text(strip=True)
            input_list.append((artist, album))
    if has_next_page == True:
        next_bowl_of_soup = get_soup(next_url)
        handle_rym_list(next_bowl_of_soup)
    return playlist_name, playlist_description, input_list

# Boomkat Bestsellers List
def handle_boomkat(soup):
    table = soup.find('div', class_='bestsellers')
    if table is None:
        print("Table not found")
    bestsellers_list = table.find('ol', class_='bestsellers-list')
    if bestsellers_list is None:
        print("List not found")
    else: 
        for item in bestsellers_list.find_all('li', class_='bestsellers-item'):
            artist = item.find('div', class_='product-name').find_all('a')[0].text.strip().title()
            album = item.find('div', class_='product-name').find_all('a')[1].text.strip()
            input_list.append((artist, album))
    playlist_name = "This Week's Boomkat Bestsellers"
    playlist_description = "For the week ending " + today
    return playlist_name, playlist_description, input_list

# Forced Exposure Bestsellers List    
def handle_forced_exposure(soup):
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
def handle_wfmu_latest(soup):
    
    # Make a selection from the available playlists
    # 1997 to Jan 2013 have different URL/content format
    # 1987-1996 only available as PDFs
    year = input("For what year (2014-present): ")
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
    return handle_wfmu_list(get_soup(sub_url))
    

def handle_wfmu_list(soup):
    date = soup.title.text[28:]
    print(date)
    playlist_name = "WFMU Heavy Play " + date
    playlist_description = ""
    for ul in soup.find_all('ul'):
        if any(li.find('strong') for li in ul.find_all('li')):
            for li in ul.find_all('li'):
                match = re.match(r'^(.*?) - (.*?) \((.*?)\)$', li.text)
                if match:
                    artist_name, album_title, record_label = match.groups()
                    input_list.append((artist_name.title(), album_title))
    return playlist_name, playlist_description, input_list
    
    
# For NTS Formatting
def format_date(date):
    day, month, year = date.split('.')
    return "20" + year + "-" + month + "-" + day

# NTS Episode TRACKS
def handle_nts_episode(soup):
    playlist_description = soup.find("div", class_="description").text
    title_info = soup.find("div", class_="bio__title")
    title = title_info.find("h1").text
    location, date = title_info.find("h2").text.split(', ')
    playlist_name = f"NTS: {title} ({date})"
    date = format_date(date)
    playlist_description = f"{playlist_description} Broadcast: {date}, {location}."
    tracklist = soup.find("ul", class_="tracklist__tracks")
    for track in tracklist:
        artist = ''
        artists = track.find_all("span", class_="track__artist")
        ## Artist is duplicated in HTML so need to prevent adding duplicates
        for other_artist in artists:
            if other_artist.text in artist:
                continue
            else:
                artist = artist + other_artist.text
            title = track.find("span", class_="track__title").text
            input_list.append((artist, title))
    return playlist_name, playlist_description, input_list

# NTS Latest Episode Selection
def handle_nts_latest(soup):
    episodes = []
    
    for episode in soup.find_all("article", class_="nts-grid-v2-item", limit=12):
        if episode:
            title = episode.find("div", class_="nts-grid-v2-item__header__title")
            if title:
                title = title.text
            details = episode.find("div", class_="nts-grid-v2-item__header-details")
            if details:
                date = details.find("span").text
                location = details.find("div").find("span", class_="text-uppercase")
                if location:
                    location = location.text
                else:
                    location = "n.l."
            episode_href = episode.find("a", class_="nts-grid-v2-item__header").get('href')
            if episode_href:
                sub_url = "https://www.nts.live" + episode_href
            episode_tags = episode.find("div", class_="nts-grid-v2-item__content").find("div", class_="nts-grid-v2-item__footer").find_all("a")
            if episode_tags:
                tags = []
                for tag in episode_tags:
                    tags.append(tag.text)
        date = format_date(date)
        episodes.append({"title": title, "date": date, "location": location, "link": sub_url, "tags": tags})
    selection = get_user_selection(episodes)
    second_bowl_of_soup = get_soup(episodes[selection-1]['link'])
    handle_nts_episode(second_bowl_of_soup)
    
