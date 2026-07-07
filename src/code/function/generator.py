import re
import torch
from transformers import pipeline

def generer_paroles(
    model,
    tokenizer,
    artiste: str,
    titre: str,
    genre: str,
    temperature: float = 0.7,
    top_k: int = 40,
    top_p: float = 0.85,
    repetition_penalty: float = 1.3,
    max_new_tokens: int = 250,
    min_new_tokens: int = 100,
) -> str:
    """Génère des paroles pour un artiste donné."""

    prompt = f"<|artiste|>{artiste}<|titre|>{titre}<|genre|>{genre}\n"

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=-1,   # CPU
    )

    result = generator(
        prompt,
        max_new_tokens=max_new_tokens,
        min_new_tokens=min_new_tokens,
        num_return_sequences=1,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,   # ← remet ça
        pad_token_id=tokenizer.eos_token_id,
        max_length=None,          # ← désactive le max_length du checkpoint
    )

    texte = result[0]["generated_text"]#.split("<|endoftext|>")[0]
    print("min_new_tokens reçu :", min_new_tokens)
    print("max_new_tokens reçu :", max_new_tokens)
    print("TEXTE BRUT :", repr(texte[:500]))
    return texte