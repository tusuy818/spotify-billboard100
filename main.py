import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup

# Obtain your Spotify App Client ID and Client Secret and export them as environment variables.
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Use Beautiful Soup 4 to scrape the Billboard Hot 100 rankings for the specified date.
input_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
url = f"https://www.billboard.com/charts/hot-100/{input_date}/"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
content = requests.get(url, headers=header).text
soup = BeautifulSoup(content, "html.parser")

# Obtain all the song names from their shared html elements.
song_rows = soup.find_all(name="div", class_="o-chart-results-list-row-container")
songs = [song.find("h3").getText().strip() for song in song_rows]

# Similarly, obtain all the artist names from their shared html elements.
artists_rows = soup.select("div.o-chart-results-list-row-container > ul.o-chart-results-list-row > li.lrv-u-width-100p > ul > li > span.a-no-trucate")
artists = [artist.getText().strip() for artist in artists_rows]

# Create the Spotify OAuth workflow and specify scope for user impersonation.
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private playlist-modify-public user-library-read"))

# Get the current user's Spotify user id.
spotify_user = sp.current_user()['id']

# Create an empty list. Use the for loop over the separate 100 songs/tracks and 100 artists lists to perform a search
# through the Spotify catalog for the exact track. Append the Spotify-specific URI of each track to the list.
tracks = []
for song, artist in zip(songs, artists):
    track = sp.search(q=f"track: {song} year: {input_date[:4]} artist: {artist}", type="track")['tracks']['items'][0]['uri']
    tracks.append(track)

# Add a new playlist, to the user's account, named after the date specified above. Then obtain the playlist id.
new_playlist = sp.user_playlist_create(user=spotify_user, name=f"{input_date} Billboard 100")
new_playlist_id = new_playlist['id']

# Using the playlist id, add all 100 songs to the new playlist.
sp.playlist_add_items(playlist_id=new_playlist_id, items=tracks)
