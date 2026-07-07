import os
from transformers import GPT2LMHeadModel, AutoTokenizer
from peft import PeftModel
import torch

# ─── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHECKPOINT    = os.path.join(BASE_DIR, "modele", "checkpoint-8000-20260707T070044Z-3-001/checkpoint-8000")
LORA_DIR      = os.path.join(BASE_DIR, "modele", "lora_adapters_2_backup")

def formater_nom(artiste: str) -> str:
    return artiste.replace("_", " ")

def get_artistes_disponibles() -> dict:
    """Retourne un dict {nom_affiche: nom_dossier}"""
    if not os.path.exists(LORA_DIR):
        return {}
    dossiers = sorted([
        d for d in os.listdir(LORA_DIR)
        if os.path.exists(os.path.join(LORA_DIR, d, "adapter_config.json"))
    ])
    return {d.replace("_", " ").replace("-", " "): d for d in dossiers}

def charger_modele(artiste: str):
    """
    Charge le checkpoint-8000 + l'adaptateur LoRA de l'artiste.
    Retourne (model, tokenizer).
    """
    tokenizer = AutoTokenizer.from_pretrained("asi/gpt-fr-cased-small")
    
    special_tokens = {
    "additional_special_tokens": [
        "<|artiste|>", "<|titre|>", "<|genre|>",
    ]
    }

    tokenizer.add_special_tokens(special_tokens)

    base = GPT2LMHeadModel.from_pretrained(
    CHECKPOINT,
    torch_dtype=torch.float32,
    )
    base.resize_token_embeddings(len(tokenizer))

    adapter_path = os.path.join(LORA_DIR, artiste)
    model = PeftModel.from_pretrained(base, adapter_path)
    model.eval()

    return model, tokenizer