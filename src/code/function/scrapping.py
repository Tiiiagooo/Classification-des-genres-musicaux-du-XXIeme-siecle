from function.utils import BeautifulSoup, requests        

def scrapping_find_lyrics(lyrics_url, headers):
    response = requests.get(lyrics_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_div = soup.find_all("div", {"class": "Lyrics-sc-37019ee2-1 jRTEBZ"})
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