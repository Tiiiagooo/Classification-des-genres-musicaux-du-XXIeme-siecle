from function.utils import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Fonction de session robuste
def requests_retry_session(retries=5, backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        allowed_methods=["GET"],
        status_forcelist=status_forcelist,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

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
    
    # Utilise la session robuste
    session = requests_retry_session()
    
    try:
        response = session.get(search_url, headers=headers, params={'q': query}, timeout=10)
        json_response = response.json()
    except Exception as e:
        print(f"Erreur pendant la requête Genius : {e}")
        return None

    song_info = None
    if json_response['response']['hits']:
        for hit in json_response['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info = hit
                break

    if song_info:
        if song_info['result']['url'].startswith("https://genius.com/"):
            lyrics_url = song_info['result']['url']
        else:
            try:
                song_api_path = song_info['result']['api_path']
                song_url = f"https://api.genius.com{song_api_path}"
                song_response = session.get(song_url, headers=headers, timeout=10)
                song_json = song_response.json()
                lyrics_path = song_json['response']['song']['path']
                lyrics_url = f"https://genius.com{lyrics_path}"
            except Exception as e:
                print(f"Erreur pendant la récupération des paroles : {e}")
                return None
        return lyrics_url
    else:
        return None    

