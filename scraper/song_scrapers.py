import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from schemas import Artist, Song

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

connection = engine.connect()

alphabet = "abcdefghijklmnopqrstuvwxyz"


def scrape_all_songs_of_all_artists_from_lyrics_dot_com():
    """
    Scrapes a song from lyrics.com

    :param song_name: song name
    :param artist_name: artist name
    :return: song lyrics
    """

    session = Session()

    for each_letter in alphabet:

        lyrics_artists_url = f"https://www.lyrics.com/artists/{each_letter}/99999"

        artists_page = requests.get(lyrics_artists_url)

        artists_soup = BeautifulSoup(artists_page.content, "html.parser")

        artists_a_elements = artists_soup.select('a[href^="artist/"]')

        for each_artist in artists_a_elements:
            print(f"For Artist: {each_artist.get_text()}")
            artist = Artist(name=each_artist.get_text())

            session.add(artist)

            songs_of_artist_url = f"https://www.lyrics.com/{each_artist['href']}"

            song_page = requests.get(songs_of_artist_url)

            songs_soup = BeautifulSoup(song_page.content, "html.parser")

            songs_a_elements = songs_soup.select('a[href^="/lyric-lf/"]')

            for each_song in songs_a_elements:
                print(f"\tSong: {each_song.get_text()}")
                lyric_of_song_url = f"https://www.lyrics.com{each_song['href']}"

                lyric_page = requests.get(lyric_of_song_url)

                lyric_soup = BeautifulSoup(lyric_page.content, "html.parser")

                lyric_text = lyric_soup.select_one("#lyric-body-text").get_text()

                song = Song(name=each_song.get_text(), lyrics=lyric_text)

                session.add(song)

            session.commit()


if __name__ == "__main__":
    scrape_all_songs_of_all_artists_from_lyrics_dot_com()
