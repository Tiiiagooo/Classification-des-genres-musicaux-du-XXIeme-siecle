from function.utils import os, json
from function.function import get_lyrics_from_genius_score
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

    result = get_lyrics_from_genius_score(song_title, artist_name, GENIUS_ACCESS_TOKEN)

    if result and result["score"] >= 1:
        # Cas : une seule URL retournée
        list_lyrics = scrapping_find_lyrics_on_genius(result["url"], headers)
        lyrics_of_song = "\n".join(list_lyrics)
        song_entry = dictionnaire_sons.setdefault(artist_name, {}).setdefault(song_title, {})
        song_entry["lyrics_primaire"] = lyrics_of_song

    else:
        # Cas : aucune URL retournée
        song_entry = dictionnaire_sons.setdefault(artist_name, {}).setdefault(song_title, {})
        song_entry["lyrics_primaire"] = None
        song_entry["type_artiste"] = None

    return dictionnaire_sons