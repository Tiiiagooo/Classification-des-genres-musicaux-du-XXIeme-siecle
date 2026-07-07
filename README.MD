# 🎤 Générateur de Paroles par Artiste — IA

> Génère des paroles de chansons dans le style d'un artiste spécifique, en combinant fine-tuning de domaine, adaptateurs LoRA par artiste, scraping automatique et interface Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface)
![PEFT](https://img.shields.io/badge/PEFT-LoRA-green?logo=huggingface)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red?logo=streamlit)
![Status](https://img.shields.io/badge/Status-MVP%20fonctionnel-brightgreen)

---

## 🎯 Objectif

Ce projet explore la génération de texte créatif appliquée à la musique française. L'idée centrale : générer des paroles cohérentes avec le style d'un artiste précis, sans modèle massif, grâce à une architecture en cascade :

```
GPT-2 français (asi/gpt-fr-cased-small)
        ↓ Fine-tuning de domaine (~1200 chansons)
Modèle spécialisé "paroles musicales FR"
        ↓ Fine-tuning LoRA par artiste (~3MB/artiste)
Adaptateur stylistique par artiste
```

Deux cas d'usage :

- **Artiste dans la base** → génération immédiate dans son style via son adaptateur LoRA
- **Artiste inconnu** → scraping automatique de ses paroles sur Genius, fine-tuning LoRA à la volée, puis génération

---

## ✨ Fonctionnalités

### Génération de paroles
- Sélection de l'artiste, du titre et du genre
- Génération via le modèle de base fine-tuné + adaptateur LoRA de l'artiste
- Paramètres de génération ajustables (temperature, top_k, top_p, repetition_penalty)
- Téléchargement des paroles générées

### Scraping & apprentissage à la demande
- Détection automatique si l'artiste est dans la base ou non
- Si absent : scraping des paroles via l'API Genius + BeautifulSoup
- Fine-tuning LoRA directement depuis l'interface Streamlit
- Barre de progression en temps réel

### Interface MVP Streamlit
- Sélection artiste avec liste déroulante (200+ artistes disponibles)
- Section "Artiste non disponible" pour scraper et entraîner un nouvel artiste
- Sidebar de paramétrage de la génération

---

## 🏗️ Architecture du projet

```
├── ngrok.exe                        # Tunnel local pour partage
├── environment.yml
├── LICENSE
├── README.md
├── src/
│   ├── code/
│   │   ├── main.py                  # MVP Streamlit
│   │   ├── notebook/
│   │   │   ├── spoti.ipynb              # Exploration données Spotify/Genius
│   │   │   ├── Recuperation_artiste.ipynb
│   │   │   ├── kaggle_dataset.ipynb
│   │   │   └── tagging.ipynb
│   │   └── function/
│   │       ├── model_loader.py      # Chargement modèle de base + LoRA
│   │       ├── generator.py         # Génération et nettoyage du texte
│   │       ├── scrapper_artiste.py  # Scraping Genius à la demande
│   │       ├── trainer_lora.py      # Fine-tuning LoRA depuis Streamlit
│   │       ├── dictionnary.py       # Gestion du corpus JSON
│   │       ├── function.py          # Fonctions utilitaires API Genius
│   │       ├── scrapping.py         # Scraping BeautifulSoup + cloudscraper
│   │       └── utils.py             # Imports partagés
│   ├── modele/
│   │   ├── checkpoint-8000/         # Modèle GPT-2 fine-tuné (~510MB)
│   │   │   ├── model.safetensors
│   │   │   ├── config.json
│   │   │   ├── tokenizer.json
│   │   │   └── ...
│   │   └── lora_adapters/           # Adaptateurs LoRA (~3MB/artiste, 165 artistes)
│   │       ├── 113/
│   │       ├── Booba/
│   │       ├── Dadju/
│   │       ├── IAM/
│   │       ├── MC_Solaar/
│   │       ├── Niska/
│   │       ├── OrelSan/
│   │       ├── Soprano/
│   │       ├── Suprême_NTM/
│   │       └── ... (165 artistes total)
│   └── data/
│       ├── json_file/
│       │   ├── final_dict_song.json     # Corpus principal (~1200 artistes)
│       │   ├── dictionnaire_artiste.json
│       │   └── ...
│       └── token/                       # Clés API
│           ├── genius_client_access_token.txt
│           ├── spotify_client_id.txt
│           └── ...
```

---

## 🧠 Choix techniques

| Composant | Choix | Justification |
|---|---|---|
| Modèle de base | `asi/gpt-fr-cased-small` (GPT-2, 124M) | Léger, français natif, fine-tunable sur Colab gratuit |
| Fine-tuning domaine | Full fine-tuning sur corpus musical | Spécialise le modèle sur le langage des paroles FR |
| Fine-tuning artiste | LoRA via PEFT | ~3MB par artiste vs 510MB full fine-tune |
| Entraînement | Google Colab (Tesla T4) | GPU gratuit pour le fine-tuning |
| Scraping | Genius API + BeautifulSoup + cloudscraper | Source la plus complète pour les paroles FR |
| Interface | Streamlit | Déploiement rapide, idéal pour MVP |
| Partage | ngrok | Tunnel local pour partager sans déploiement cloud |

---

## 📊 Résultats

| Métrique | Valeur |
|---|---|
| Validation loss (checkpoint-8000) | 2.77 |
| Perplexité finale | ~16 |
| Artistes entraînés (LoRA) | 165 |
| Chansons dans le corpus | ~8000 |
| Taille adaptateur LoRA moyen | ~3MB |

---

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/Tiiiagooo/Classification-des-genres-musicaux-du-XXIeme-siecle.git
cd Classification-des-genres-musicaux-du-XXIeme-siecle

# Créer l'environnement conda
conda create -n mvp_lyrics python=3.10 -y
conda activate mvp_lyrics

# Installer les dépendances
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers peft streamlit datasets cloudscraper beautifulsoup4 requests pyphen
```

### Lancer le MVP

```bash
streamlit run src/code/main.py --server.fileWatcherType none
```

### Partager via ngrok

```bash
# Terminal 1
streamlit run src/code/main.py --server.fileWatcherType none

# Terminal 2
ngrok.exe http 8501
```

---

## 🗺️ Roadmap

- [x] Scraping corpus paroles (Genius API + BeautifulSoup)
- [x] Fine-tuning GPT-2 français sur corpus musical (~1200 artistes)
- [x] SmartSaveCallback — sauvegarde intelligente par seuil de loss adaptatif
- [x] Fine-tuning LoRA par artiste (~200 artistes entraînés)
- [x] MVP Streamlit — génération par artiste
- [x] Scraping à la demande depuis l'interface
- [x] Fine-tuning LoRA depuis l'interface Streamlit
- [x] Partage via ngrok
- [ ] Finir l'entraînement LoRA sur les 1200 artistes du corpus
- [ ] Stats stylistiques par artiste injectées dans le prompt
- [ ] Module collaboratif — correction et enrichissement du corpus
- [ ] Déploiement cloud (Streamlit Cloud / AWS)
- [ ] RLHF avec reward function automatique (rimes + syllabes)
- [ ] Passage à un modèle plus gros (GPT-2 medium ou LLaMA)

---

## 💡 Approche technique détaillée

### Transfer learning en cascade

Le projet utilise un entraînement en trois phases :

1. **Pré-entraînement général** — `asi/gpt-fr-cased-small` connaît le français
2. **Fine-tuning de domaine** — spécialisation sur le vocabulaire et la structure des paroles musicales FR (domain adaptation)
3. **Fine-tuning de style** — adaptateur LoRA par artiste, entraîné uniquement sur ses chansons (parameter-efficient fine-tuning)

### Tokens spéciaux

```
<|artiste|>Dadju<|titre|>Jaloux<|genre|>rnb
[Couplet 1]
paroles...
<|endoftext|>
```

### Callbacks d'entraînement custom

- `SmartSaveCallback` — sauvegarde uniquement si la loss baisse de manière significative (seuil adaptatif selon le niveau de loss)
- `StopOnLossCallback` — arrêt automatique quand la loss cible est atteinte
- `CheckpointLoraCallback` — sauvegarde intermédiaire LoRA pour reprendre après coupure Colab

---

## 🛠️ Stack

`Python 3.10` `PyTorch` `Hugging Face Transformers` `PEFT / LoRA` `Streamlit` `Genius API` `BeautifulSoup` `cloudscraper` `pyphen` `ngrok`

---

## 📄 Licence

CC0-1.0 — libre d'utilisation
