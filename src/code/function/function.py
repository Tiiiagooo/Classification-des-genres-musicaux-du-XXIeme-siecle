from function.utils import requests
import re, unicodedata
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry



def slug(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

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
    
def get_lyrics_from_genius(song_title, artist_name, GENIUS_ACCESS_TOKEN ):
    """
    Cette fonction prend en entrée le titre d'une chanson, le nom d'un artiste et les access token de l'API GENIUS,  
    et retourne un lien URL des paroles de la chanson sur genius.

    Parameter :
    - song_title (str) : Titre de la chanson.
    - artist_name (str) : Nom de l'artiste.
    - GENIUS_ACCESS_TOKEN (str) : Clé API d'accès à Genius.

    Return :
    - lyrics_url (str) : URL des paroles si une correspondance est trouvée.
    - list_of_url (list[str]) : Liste d'URLs similaires si aucun match direct.
    - type_artiste : Si l'artiste est celui qu'on voulait ou non.
    - primary_artist : Pour le nom de l'artiste
    - None : Si aucune correspondance n'est trouvée.
    """
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    search_url = "https://api.genius.com/search"
    queries = [f"{song_title} {artist_name}", song_title]
    
    # Utilise la session robuste
    session = requests_retry_session()

    try:
        responses = [session.get(search_url, headers=headers, params={'q': q}, timeout=10) for q in queries]
        json_responses = [r.json() for r in responses]

    except Exception as e:
        print(f"Erreur pendant la requête Genius : {e}")
        return None, None, None
    
    for json_response in json_responses:
        hits = json_response.get('response', {}).get('hits', [])
        for hit in hits:
            primary_artist = hit['result']['primary_artist']['name'].lower()

            #Si le chanteur est trouvé
            if artist_name.lower() in primary_artist:
                try:
                    url = hit['result']['url']
                    if url.startswith("https://genius.com/"):
                        return url, "artiste_primaire", primary_artist
                    else:
                        # Fallback: récupérer via l'API song
                        song_api_path = hit['result']['api_path']
                        song_url = f"https://api.genius.com{song_api_path}"
                        song_response = session.get(song_url, headers=headers, timeout=10)
                        song_json = song_response.json()
                        lyrics_path = song_json['response']['song']['path']
                        return f"https://genius.com{lyrics_path}", "artiste_primaire", primary_artist
                except Exception as e:
                    print(f"Erreur pendant la récupération des paroles : {e}")
                    return None, None, None

        #Si la musique n'a pas été trouvé, on cherche les autres titres similaires            
        alternative_hits = json_responses[1].get('response', {}).get('hits', []) #json_responses[1] pour la 2ème méthode de la requete qui contient que le titre

        list_of_url = [
            hit['result']['url']
            for hit in alternative_hits
            if hit['result']['url'].startswith("https://genius.com/")
        ]
        list_of_artiste = [hit['result']['primary_artist']['name'].lower() for hit in alternative_hits]

    return list_of_url, "artiste_secondaire", list_of_artiste if list_of_url else None        
   

