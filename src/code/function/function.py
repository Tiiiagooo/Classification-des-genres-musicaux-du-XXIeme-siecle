from function.utils import requests

def get_token(liste_txt_file):
    """
    Cette fonction prend en entrée une liste de chemin de fichier '.txt',  
    contenant les différents access token des différents API.  
    Et retourne les access token des API en type str.

    Parameter :
    - liste_txt_files (list) : Liste des fichiers d'un dossier.  

    Return :
    - genius_token (str) : le contenu écrit dans le fichier portant le nom 'genius_client_access_token'
    - spotify_id (str) : le contenu écrit dans le fichier portant le nom 'spotify_client_id'
    - spotify_secret (str) : le contenu écrit dans le fichier portant le nom 'spotify_client_secret'
    - ValueError : Si un fichier ne contient pas les access token
    """
    genius_token = None
    spotify_id = None
    spotify_secret = None

    for file_path in liste_txt_file:
        with open(file_path, 'r') as file:
            content = file.read()
            if 'genius_client_access_token' in file_path.lower():
                genius_token = content
            elif 'spotify_client_id' in file_path.lower():
                spotify_id = content
            elif 'spotify_client_secret' in file_path.lower():
                spotify_secret = content
    if None in (genius_token, spotify_id, spotify_secret):
        raise ValueError("Certaines variables n'ont pas été correctement assignées. Vérifiez les fichiers dans le répertoire.")
    else:
        return genius_token, spotify_id, spotify_secret
    
def get_lyrics_from_genius(song_title, artist_name,GENIUS_ACCESS_TOKEN ):
    """
    Cette fonction prend en entrée le titre d'une chanson, le nom d'un artiste et les access token de l'API GENIUS,  
    et retourne un lien URL des paroles de la chanson sur genius.

    Parameter :
    - song_title (str) : Le titre de la chanson.
    - artist_name (str) : Le nom de l'artiste.
    - GENIUS_ACCESS_TOKEN (str) : Clé d'API Genius pour l'authentification.

    Return :
    - lyrics_url (str) : L'URL Genius des paroles de la chanson si trouvée.
    - None : Si aucune correspondance n'est trouvée.
    """
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    search_url = "https://api.genius.com/search"
    query = f"{song_title} {artist_name}"
    response = requests.get(search_url, headers=headers, params={'q': query})
    json_response = response.json()
    song_info = None
    if json_response['response']['hits']:
        for hit in json_response['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info = hit
                break
    if song_info:
        song_api_path = song_info['result']['api_path']
        song_url = f"https://api.genius.com{song_api_path}"
        song_response = requests.get(song_url, headers=headers)
        song_json = song_response.json()
        lyrics_path = song_json['response']['song']['path']
        lyrics_url = f"https://genius.com{lyrics_path}"
        return lyrics_url
    else:
        return None
    

