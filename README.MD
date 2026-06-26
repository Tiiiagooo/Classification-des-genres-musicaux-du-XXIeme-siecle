# 🎵 Générateur de Paroles de Chansons par IA

> Génère des paroles de chansons dans le style d'un artiste ou d'un genre musical, en combinant scraping, fine-tuning léger et interface collaborative.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow?logo=huggingface)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red?logo=streamlit)
![Status](https://img.shields.io/badge/Status-En%20cours-orange)

---

## 🎯 Objectif

Ce projet explore la génération de texte créatif appliquée à la musique. L'idée centrale : permettre à n'importe qui de générer des paroles cohérentes avec le style d'un artiste ou d'un genre musical, sans avoir besoin d'un modèle massif.

Deux cas d'usage principaux :

- **Artiste connu** → le modèle génère directement des paroles dans son style
- **Artiste inconnu** → le système scrape ses paroles, se fine-tune dessus, puis génère

---

## ✨ Fonctionnalités

### Génération de paroles
- Entrée : nom d'artiste + genre souhaité
- Détection automatique si l'artiste est dans la base ou non
- Si absent : scraping automatique des paroles via APIs (Genius, etc.), nettoyage et fine-tuning rapide
- Génération de paroles cohérentes avec le style détecté

### Classification collaborative des genres
- Classification initiale sur genres principaux (pop, rap, rock, R&B...)
- **Système collaboratif** : les utilisateurs peuvent reclassifier et affiner les sous-genres
- Prise en compte des sous-genres (trap, lo-fi, drill, afrobeats...) souvent ignorés par les datasets classiques
- Base de données enrichie au fil des contributions

### Interface
- MVP Streamlit (en cours)
- Saisie artiste / genre
- Affichage des paroles générées
- Module de reclassification collaborative

---

## 🏗️ Architecture

```
├── src/
│   ├── code/
│   │   ├── spoti.ipynb          # Collecte et exploration des données Spotify/Genius
│   │   └── function/
│   │       └── function.py      # Fonctions utilitaires (scraping, nettoyage, tokenisation)
│   └── data/
│       └── documentation/
│           └── Etat_de_lart.pdf # État de l'art — modèles génératifs et NLP musical
├── environment.yml              # Dépendances conda
└── README.md
```

---

## 🧠 Choix techniques

| Composant | Choix | Justification |
|---|---|---|
| Modèle génératif | GPT-2 / Mistral (quantifié) | Léger, fine-tunable rapidement sur CPU/GPU modeste |
| Fine-tuning | LoRA / QLoRA (PEFT) | Adapte le modèle sans réentraîner tous les poids |
| Scraping paroles | Genius API + BeautifulSoup | Source de paroles la plus complète |
| Évaluation | Perplexité, BLEU, ROUGE | Métriques standards pour la génération de texte |
| Interface | Streamlit | Déploiement rapide, idéal pour MVP |

---

## 📊 Résultats actuels

| Métrique | Valeur |
|---|---|
| Validation loss (min observé) | 2.83 |
| Cohérence stylistique | Évaluation qualitative en cours |
| Genres couverts | 8 genres principaux + sous-genres en cours |

---

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/Tiiiagooo/Classification-des-genres-musicaux-du-XXIeme-siecle.git
cd Classification-des-genres-musicaux-du-XXIeme-siecle

# Créer l'environnement conda
conda env create -f environment.yml
conda activate music-gen

# Lancer le notebook d'exploration
jupyter notebook src/code/spoti.ipynb
```

---

## 🗺️ Roadmap

- [x] Collecte et exploration des données (Spotify, Genius)
- [x] Pipeline de nettoyage et tokenisation des paroles
- [x] Fine-tuning GPT-2 sur corpus par genre
- [x] Fine-tuning Mistral avec LoRA/QLoRA
- [ ] Système de détection artiste + scraping automatique à la volée
- [ ] Module de reclassification collaborative des sous-genres
- [ ] Interface Streamlit complète
- [ ] Déploiement cloud (AWS / GCP)

---

## 💡 Pourquoi ce projet ?

Les datasets musicaux publics se limitent souvent à 6-10 genres génériques. Or la réalité musicale est bien plus granulaire : entre le rap et le trap, entre la pop et la hyperpop, les nuances stylistiques sont immenses. Ce projet cherche à construire un système qui évolue avec les usages réels, grâce à la contribution collaborative des utilisateurs.

---

## 🛠️ Stack

`Python` `PyTorch` `Hugging Face Transformers` `PEFT / LoRA` `Streamlit` `Genius API` `Pandas` `Scikit-Learn`

---

## 📄 Licence

CC0-1.0 — libre d'utilisation
