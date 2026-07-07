import os
import json
import glob
from function.function import get_token, get_lyrics_from_genius_score
from function.scrapping import scrapping_find_lyrics_on_genius

# ─── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH_TOKEN = os.path.join(BASE_DIR, "data", "token", "*")
PATH_JSON  = os.path.join(BASE_DIR, "data", "json_file")
CORPUS_PATH = os.path.join(PATH_JSON, "final_dict_song.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def get_genius_token() -> str:
    token_files = glob.glob(PATH_TOKEN)
    print("PATH_TOKEN :", PATH_TOKEN)
    print("Fichiers trouvés :", token_files)
    
    for file_path in token_files:
        print("  →", file_path)
        if "genius_client_access_token" in file_path.lower():
            with open(file_path, "r") as f:
                return f.read().strip()
    
    raise ValueError("Fichier genius_client_access_token introuvable")

def charger_corpus() -> dict:
    """Charge le corpus existant."""
    if os.path.exists(CORPUS_PATH):
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_corpus(corpus: dict):
    """Sauvegarde le corpus."""
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

def scraper_artiste(artiste: str, nb_chansons: int = 10, log_fn=None) -> dict:
    """
    Scrape les chansons d'un artiste depuis Genius.
    Retourne le dict des chansons scrapées.
    """

    if log_fn is None:
        log_fn = print

    token = get_genius_token()
    corpus = charger_corpus()

    # Vérifie si l'artiste existe déjà dans le corpus
    if artiste in corpus:
        print(f"✅ {artiste} déjà dans le corpus ({len(corpus[artiste])} chansons)")
        return corpus[artiste]

    print(f"🔍 Scraping de {artiste}...")
    chansons_trouvees = {}

    # Recherche les chansons de l'artiste sur Genius
    import requests
    headers_api = {"Authorization": f"Bearer {token}"}
    session_url = f"https://api.genius.com/search"

    response = requests.get(
        session_url,
        headers=headers_api,
        params={"q": artiste},
        timeout=10
    ).json()

    hits = response.get("response", {}).get("hits", [])

    for hit in hits[:nb_chansons]:
        primary_artist = hit["result"]["primary_artist"]["name"].lower()

        if artiste.lower() not in primary_artist:
            continue

        song_title = hit["result"]["title"]
        song_url   = hit["result"]["url"]

        print(f"   📀 {song_title}")
        log_fn(f"📀 {song_title}") 

        try:
            list_lyrics = scrapping_find_lyrics_on_genius(song_url, HEADERS)
            if not list_lyrics:
                continue

            lyrics = "\n".join(list_lyrics)
            chansons_trouvees[song_title] = {
                "prompt": f"Artiste: {artiste}\nTitre: {song_title}\nGenre: rap",
                "completion": lyrics
            }
        except Exception as e:
            print(f"   ⚠️ Erreur sur {song_title} : {e}")
            continue

    # Sauvegarde dans le corpus
    if chansons_trouvees:
        corpus[artiste] = chansons_trouvees
        sauvegarder_corpus(corpus)
        print(f"✅ {len(chansons_trouvees)} chansons scrapées pour {artiste}")
    else:
        print(f"❌ Aucune chanson trouvée pour {artiste}")

    return chansons_trouvees