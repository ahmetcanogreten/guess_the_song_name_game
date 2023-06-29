import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from .schemas import Artist, Song

url = URL.create(
    drivername="postgresql",
    host="localhost",
    port=5432,
    username="postgres",
    password="postgres",
    database="postgres",
)

engine = create_engine(url)

Session = sessionmaker(bind=engine)

session = Session()

alphabet = "abcdefghijklmnopqrstuvwxyz"


async def scrape_song(song_url):
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(song_url) as response:
            song_content = await response.text()
            song_soup = BeautifulSoup(song_content, "html.parser")
            lyric_text = song_soup.select_one("#lyric-body-text").get_text()
            return lyric_text


async def scrape_songs_of_artist(artist, artist_url):
    async with aiohttp.ClientSession() as client_session:
        async with client_session.get(artist_url) as response:
            artist_content = await response.text()
            artist_soup = BeautifulSoup(artist_content, "html.parser")
            songs_a_elements = artist_soup.select('a[href^="/lyric-lf/"]')
            tasks = []
            for each_song in songs_a_elements:
                song_name = each_song.get_text()
                song_url = f"https://www.lyrics.com{each_song['href']}"
                task = asyncio.ensure_future(scrape_song(song_url))
                tasks.append(task)
            song_lyrics = await asyncio.gather(*tasks)
            for song_name, lyric_text in zip(songs_a_elements, song_lyrics):
                song = Song(name=song_name, lyrics=lyric_text)
                artist.songs.append(song)


async def scrape_all_songs_of_all_artists_from_lyrics_dot_com():
    async with aiohttp.ClientSession() as client_session:
        for each_letter in alphabet:
            artists_url = f"https://www.lyrics.com/artists/{each_letter}/1"
            async with client_session.get(artists_url) as response:
                artists_content = await response.text()
                artists_soup = BeautifulSoup(artists_content, "html.parser")
                artists_a_elements = artists_soup.select('a[href^="artist/"]')
                tasks = []
                for each_artist in artists_a_elements:
                    artist_name = each_artist.get_text()
                    artist = Artist(name=artist_name)
                    session.add(artist)
                    artist_url = f"https://www.lyrics.com/{each_artist['href']}"
                    task = asyncio.ensure_future(
                        scrape_songs_of_artist(artist, artist_url)
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)
    session.commit()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_all_songs_of_all_artists_from_lyrics_dot_com())
