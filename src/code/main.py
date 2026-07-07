import streamlit as st
import torch
from function.model_loader import charger_modele, get_artistes_disponibles
from function.generator import generer_paroles
from function.scrapper_artiste import charger_corpus, scraper_artiste
import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

# ─── Cache modèle ─────────────────────────────────────────────────────────────
@st.cache_resource
def charger_modele_cache(artiste: str):
    return charger_modele(artiste)

# ─── Config page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Générateur de paroles",
    page_icon="🎤",
    layout="centered"
)

st.title("🎤 Générateur de paroles")
st.caption("Fine-tuning GPT-2 français + LoRA par artiste")

# ─── Sidebar — paramètres de génération ───────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Paramètres")
    temperature        = st.slider("Temperature",        0.5, 1.0, 0.7, 0.05)
    top_k              = st.slider("Top K",              10,  100, 40,  5)
    top_p              = st.slider("Top P",              0.5, 1.0, 0.85, 0.05)
    repetition_penalty = st.slider("Repetition penalty", 1.0, 2.0, 1.3, 0.1)
    max_new_tokens     = st.slider("Longueur max",       50,  400, 250, 50)
    min_new_tokens     = st.slider("Longueur min",  50, 200, 100, 10)

# ─── Formulaire principal ─────────────────────────────────────────────────────
artistes_dict   = get_artistes_disponibles()
artiste_affiche = st.selectbox("🎙️ Artiste", list(artistes_dict.keys()),index=None, placeholder="Select artiste")
if artiste_affiche:
    artiste         = artistes_dict[artiste_affiche]
    titre   = st.text_input("🎵 Titre de la chanson", placeholder="Mon titre")
    genre   = st.selectbox("🎸 Genre", ["rap", "rnb", "pop", "variété", "reggae"])

    # ─── Génération ───────────────────────────────────────────────────────────────
    if st.button("🎶 Générer", type="primary"):
        if not titre:
            st.warning("Entre un titre pour la chanson")
        else:
            with st.spinner(f"Génération en cours pour {artiste}..."):
                model, tokenizer = charger_modele_cache(artiste)
                paroles = generer_paroles(
                    model, tokenizer,
                    artiste, titre, genre,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    repetition_penalty=repetition_penalty,
                     max_new_tokens=max_new_tokens,
                     min_new_tokens=min_new_tokens,
                )

            st.subheader("📝 Paroles générées")
            st.text_area("", paroles, height=400)
            st.download_button(
                label="💾 Télécharger",
                data=paroles,
                file_name=f"{artiste}_{titre}.txt",
                mime="text/plain"
            )
else:
    st.info("👆 Sélectionne un artiste pour commencer")

# ─── Artiste inconnu ──────────────────────────────────────────────────────────
st.divider()
st.subheader("🔍 Artiste non disponible ?")

artiste_nouveau = st.text_input("Nom de l'artiste à scraper", placeholder="Ex: Ninho")

if st.button("🔎 Scraper cet artiste"):
    if not artiste_nouveau:
        st.warning("Entre un nom d'artiste")
    else:
        corpus = charger_corpus()
        if artiste_nouveau in corpus:
            nb_chansons_dispo = len(corpus[artiste_nouveau])
            st.info(f"ℹ️ {artiste_nouveau} déjà dans le corpus avec {nb_chansons_dispo} chansons.")
            st.warning("Lance l'entraînement ci-dessous.")
            st.session_state["chansons_scrapees"] = corpus[artiste_nouveau]
            st.session_state["artiste_nouveau"]   = artiste_nouveau
        else:
            with st.spinner(f"Scraping de {artiste_nouveau} en cours..."):
                log_container = st.empty()
                logs = []

                def log_streamlit(message: str):
                    logs.append(message)
                    log_container.markdown("\n\n".join(logs))

                chansons = scraper_artiste(
                    artiste_nouveau,
                    nb_chansons=20,
                    log_fn=log_streamlit   # ← passe la fonction
                )

            if chansons:
                st.session_state["chansons_scrapees"] = chansons
                st.session_state["artiste_nouveau"]   = artiste_nouveau
                st.success(f"✅ {len(chansons)} chansons récupérées pour {artiste_nouveau}")
            else:
                st.error(f"❌ Aucune chanson trouvée pour {artiste_nouveau}")

# ─── Bloc entraînement — affiché si chansons en session ──────────────────────
if "chansons_scrapees" in st.session_state:
    chansons      = st.session_state["chansons_scrapees"]
    artiste_train = st.session_state["artiste_nouveau"]
    nb            = len(chansons)

    if nb >= 5:
        st.info(f"🎵 {nb} chansons disponibles pour {artiste_train}")
        st.warning("⚠️ L'entraînement sur CPU peut prendre 30-60 minutes.")

        # Initialise l'état
        if "entrainement_en_cours" not in st.session_state:
            st.session_state["entrainement_en_cours"] = False

        if st.button(
            "🚀 Lancer l'entraînement LoRA",
            type="primary",
            disabled=st.session_state["entrainement_en_cours"]  # ← grisé si en cours
        ):
            st.session_state["entrainement_en_cours"] = True
            from function.trainer_lora import entrainer_lora

            _, tokenizer_train = charger_modele_cache(
                list(artistes_dict.values())[0]
            )

            progress_bar = st.progress(0)
            status_text  = st.empty()
            loss_text    = st.empty()

            def update_progress(epoch, loss):
                progress = min(float(epoch) / 50, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"⏳ Epoch {epoch:.0f}/50")
                loss_text.text(f"📉 Loss actuelle : {loss:.4f}")

            entrainer_lora(
                artiste_train,
                chansons,
                tokenizer_train,
                target_loss=2.6,
                progress_callback=update_progress
            )

            st.success(f"✅ {artiste_train} entraîné et disponible !")
            st.info("🔄 Rafraîchis la page pour voir l'artiste dans la liste")
            del st.session_state["chansons_scrapees"]
            del st.session_state["artiste_nouveau"]
    else:
        st.warning(f"⚠️ Seulement {nb} chansons — minimum 5 requis")