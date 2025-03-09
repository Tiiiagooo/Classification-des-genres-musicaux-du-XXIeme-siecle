from function.utils import os, json
from function.function import get_lyrics_from_genius
from function.scrapping import scrapping_find_lyrics

def get_dictionnary(PATH_JSON, dictionnary_name):
    if os.path.exists(PATH_JSON+dictionnary_name):
        with open(PATH_JSON+dictionnary_name, "r") as json_file:
            dictionnaire = json.load(json_file)
    else:
        dictionnaire = dict()
        with open(PATH_JSON+dictionnary_name, "w") as json_file:
            json.dump(dictionnaire, json_file, indent=4)
    return dictionnaire

def update_dictionnary(song_title, artist_name, GENIUS_ACCESS_TOKEN, dictionnaire_song, headers):
    lyrics_url = get_lyrics_from_genius(song_title, artist_name, GENIUS_ACCESS_TOKEN)
    if lyrics_url:
        list_lyrics = scrapping_find_lyrics(lyrics_url, headers)
        lyrics_of_song = "\n".join(list_lyrics)
        dictionnaire_song.setdefault(artist_name, {}).setdefault(song_title, {})["lyrics"] = lyrics_of_song
    else:
        #   print(f"Lyrics de {artist_name} pour '{song_title}' not found on Genius.")
        dictionnaire_song.setdefault(artist_name, {}).setdefault(song_title, {})["lyrics"] = None
    return dictionnaire_song