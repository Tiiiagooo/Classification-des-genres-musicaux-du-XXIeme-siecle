from function.utils import os, json

def get_dictionnary(PATH_JSON):
    if os.path.exists(PATH_JSON+"dictionnaire_song.json"):
        with open(PATH_JSON+"dictionnaire_song.json", "r") as json_file:
            dictionnaire_song = json.load(json_file)
    else:
        dictionnaire_song = dict()
        with open(PATH_JSON+"dictionnaire_song.json", "w") as json_file:
            json.dump(dictionnaire_song, json_file, indent=4)
    return dictionnaire_song