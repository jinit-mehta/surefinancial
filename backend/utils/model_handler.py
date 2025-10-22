import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def detect_device():
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def load_model(model_name="t5-small", quantized_path=None):
    device = detect_device()
    # Try quantized path first (user-provided)
    try:
        if quantized_path:
            # user would place quantized weights here; loading method depends on quantization
            model = AutoModelForSeq2SeqLM.from_pretrained(quantized_path, device_map="auto")
            tokenizer = AutoTokenizer.from_pretrained(quantized_path)
            return tokenizer, model, device
    except Exception:
        pass
    # fallback: small CPU model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.to(device)
    return tokenizer, model, device

def summarize_text(tokenizer, model, device, text, max_length=128):
    input_ids = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).input_ids.to(device)
    outputs = model.generate(input_ids, max_length=max_length)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
