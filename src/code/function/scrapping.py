from function.utils import BeautifulSoup, requests        

def scrapping_find_lyrics_on_genius(lyrics_url, headers):
    response = requests.get(lyrics_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_div = soup.find_all("div", {"class": "Lyrics-sc-37019ee2-1 jRTEBZ"})
    if not lyrics_div:
        lyrics_div = soup.find_all("div", {"class": "Lyrics__Container-sc-3d1d18a3-1 bjajog"})
    else:
        print("Parole pas dans la bonne div")
        return []

    liste_parole = []
    for div in lyrics_div:
        header = div.find("div", class_="LyricsHeader__Container-sc-d6abeb2b-1")
        if header:
            header.decompose()  # Supprime le bloc d'en-tête

        texte = div.get_text(separator="\n").strip()
        if texte:
            liste_parole.append(texte)
    return liste_parole

def scrapping_find_lyrics_on_lyricsfind(lyrics_url, headers):
    response = requests.get(lyrics_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_div = soup.find_all("div", {"class": "MuiBox-root css-0"})
    liste_parole = [div.get_text(separator="\n").strip() for div in lyrics_div]
    return liste_parole

def get_url(URL_BASE, years, headers):
    response = requests.get(URL_BASE+"annee/"+years, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    pagination_links = soup.find_all("a", class_="pagination")
    next_pages = [URL_BASE+link.get("href") for link in pagination_links if link.get("href")]
    if not next_pages:
        return [URL_BASE + "annee/" + str(years)]

    return next_pages

def scrapping_artiste(URL, headers):
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    artiste_div = soup.find_all("span", class_="single-artiste")
    liste_artiste = [artiste.get_text().strip() for artiste in artiste_div]
    return liste_artiste