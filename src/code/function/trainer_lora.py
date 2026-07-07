import os
import torch
from transformers import (
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
    TrainerCallback
)
from peft import get_peft_model, LoraConfig, TaskType
from datasets import Dataset
from function.model_loader import CHECKPOINT, LORA_DIR
import re

# ─── Config LoRA ──────────────────────────────────────────────────────────────
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["c_attn", "c_proj"],
)

class StopOnLossCallback(TrainerCallback):
    def __init__(self, target_loss: float = 2.6):
        self.target_loss = target_loss

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        current_loss = logs.get("loss")
        if current_loss and current_loss <= self.target_loss:
            print(f"🎯 Loss cible atteinte ({current_loss:.4f}) — arrêt")
            control.should_training_stop = True

def entrainer_lora(
    artiste: str,
    chansons: dict,
    tokenizer,
    target_loss: float = 2.6,
    progress_callback=None   # fonction appelée à chaque epoch pour Streamlit
):
    """
    Entraîne un adaptateur LoRA pour un artiste.
    progress_callback(epoch, loss) → pour mettre à jour la progress bar Streamlit
    """
    adapter_path = os.path.join(LORA_DIR, artiste.replace(" ", "_").replace("/", "-"))

    # if os.path.exists(os.path.join(adapter_path, "adapter_config.json")):
    #     print(f"✅ Adaptateur déjà existant pour {artiste}")
    #     return adapter_path

    # 1. Prépare les données
    artist_data = []
    for title, song_data in chansons.items():
        if not song_data.get("completion"):
            continue
        try:
            genre = song_data['prompt'].split('Genre:')[1].strip()
        except (KeyError, IndexError):
            genre = "inconnu"
        text = (
            f"<|artiste|>{artiste}<|titre|>{title}<|genre|>{genre}\n"
            f"{song_data['completion']}<|endoftext|>"
        )
        artist_data.append({"text": text})

    if not artist_data:
        raise ValueError(f"Aucune parole disponible pour {artiste}")

    raw = Dataset.from_list(artist_data)
    tokenized = raw.map(
        lambda x: tokenizer(x["text"], truncation=True, max_length=512),
        batched=True, remove_columns=["text"]
    )

    # 2. Charge le modèle base + LoRA
    base_model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT, torch_dtype=torch.float32
    )
    base_model.resize_token_embeddings(len(tokenizer))
    lora_model = get_peft_model(base_model, lora_config)

    # 3. Callback progress Streamlit
    class ProgressCallback(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kwargs):
            if logs and progress_callback:
                loss = logs.get("loss", 0)
                progress_callback(state.epoch, loss)

    # 4. Entraînement
    tmp_dir = f"/tmp/lora_{artiste.replace(' ', '_')}"
    training_args = TrainingArguments(
        output_dir=tmp_dir,
        num_train_epochs=50,
        per_device_train_batch_size=2,   # petit batch pour CPU
        learning_rate=5e-4,
        warmup_steps=10,
        weight_decay=0.01,
        save_strategy="no",
        logging_steps=1,   # ← log à chaque step au lieu de 5
        fp16=False,                       # pas de fp16 sur CPU
        report_to="none",
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=lora_model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=data_collator,
        callbacks=[
            StopOnLossCallback(target_loss=target_loss),
            ProgressCallback(),
        ],
    )
    trainer.train()

    # 5. Sauvegarde
    os.makedirs(adapter_path, exist_ok=True)
    lora_model.save_pretrained(adapter_path)
    print(f"💾 Adaptateur sauvegardé → {adapter_path}")

    return adapter_path