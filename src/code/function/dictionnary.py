from function.utils import os, json

def get_dictionnary(PATH_JSON, dictionnary_name):
    if os.path.exists(PATH_JSON+dictionnary_name):
        with open(PATH_JSON+dictionnary_name, "r") as json_file:
            dictionnaire = json.load(json_file)
    else:
        dictionnaire = dict()
        with open(PATH_JSON+dictionnary_name, "w") as json_file:
            json.dump(dictionnaire, json_file, indent=4)
    return dictionnaire