from function.utils import BeautifulSoup, requests        

def scrapping_find_lyrics(lyrics_url, headers):
    response = requests.get(lyrics_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_div = soup.find_all("div", {"class": "Lyrics-sc-37019ee2-1 jRTEBZ"})
    liste_parole = [div.get_text(separator="\n").strip() for div in lyrics_div]
    return liste_parole