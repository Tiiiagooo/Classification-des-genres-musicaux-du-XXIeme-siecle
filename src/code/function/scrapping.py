from function.utils import BeautifulSoup, requests        
import cloudscraper


def scrapping_find_lyrics_on_genius(lyrics_url, headers):
    # Création du scraper avec user agent Firefox
    scraper = cloudscraper.create_scraper()
    response = scraper.get(lyrics_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_divs = soup.select('div[data-lyrics-container="true"]')    
    if not lyrics_divs:
        return []

    liste_parole = []

    for div in lyrics_divs:
        header = soup.select('div[data-exclude-from-selection="true"]')
        if header:
            for head in header:
                head.decompose() # Supprime le bloc d'en-tête
        for br in div.find_all("br"):
            br.replace_with("\n")

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