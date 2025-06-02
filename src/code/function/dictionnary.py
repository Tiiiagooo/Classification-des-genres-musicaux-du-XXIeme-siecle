from function.utils import os, json
from function.function import get_lyrics_from_genius
from function.scrapping import scrapping_find_lyrics_on_genius

def get_dictionnary(PATH_JSON, dictionnary_name):
    if os.path.exists(PATH_JSON+dictionnary_name):
        with open(PATH_JSON+dictionnary_name, "r") as json_file:
            dictionnaire = json.load(json_file)
    else:
        dictionnaire = dict()
        with open(PATH_JSON+dictionnary_name, "w") as json_file:
            json.dump(dictionnaire, json_file, indent=4)
    return dictionnaire

def update_dictionary(song_title, artist_name, GENIUS_ACCESS_TOKEN, dictionnaire_sons, headers):
    """
    Met à jour un dictionnaire contenant les paroles de chansons récupérées depuis Genius.

    Paramètres :
    - song_title (str) : Titre de la chanson.
    - artist_name (str) : Nom de l'artiste.
    - GENIUS_ACCESS_TOKEN (str) : Token d'accès à l'API Genius.
    - dictionnaire_sons (dict) : Dictionnaire contenant les paroles.
    - headers (dict) : En-têtes HTTP pour le scraping.

    Retour :
    - dictionnaire_sons (dict) : Dictionnaire mis à jour.
    """

    lyrics_url, type_artiste, artiste, titre = get_lyrics_from_genius(song_title, artist_name, GENIUS_ACCESS_TOKEN)

    if isinstance(lyrics_url, str):
        # Cas : une seule URL retournée
        list_lyrics = scrapping_find_lyrics_on_genius(lyrics_url, headers)
        lyrics_of_song = "\n".join(list_lyrics)
        song_entry = dictionnaire_sons.setdefault(artist_name, {}).setdefault(song_title, {})
        song_entry["lyrics_primaire"] = lyrics_of_song
        song_entry["type_artiste"] = type_artiste

    elif isinstance(lyrics_url, list):
        # Cas : plusieurs URLs (résultats alternatifs)
        for idx, url in enumerate(lyrics_url[:5]):
            if artiste[idx] == "genius":
                continue
            list_lyrics = scrapping_find_lyrics_on_genius(url, headers)
            lyrics_of_song = "\n".join(list_lyrics)
            song_entry = dictionnaire_sons.setdefault(artist_name, {}).setdefault(song_title, {})
            key_lyrics = f"lyrics_{idx}"
            key_type = f"type_artiste_{idx}"
            secondary_artiste = f"artiste_{idx}"
            title = f"title_{idx}"
            song_entry["lyrics_primaire"] = None
            song_entry["type_artiste"] = None
            song_entry[key_type] = type_artiste
            song_entry[secondary_artiste] = artiste[idx]
            song_entry[title] = titre[idx]
            song_entry[key_lyrics] = lyrics_of_song

            # On arrête si les paroles mentionnent l'artiste
            if artist_name.lower() in lyrics_of_song.lower():
                break

    else:
        # Cas : aucune URL retournée
        song_entry = dictionnaire_sons.setdefault(artist_name, {}).setdefault(song_title, {})
        song_entry["lyrics_primaire"] = None
        song_entry["type_artiste"] = None

    return dictionnaire_sons