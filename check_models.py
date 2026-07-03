"""
check_models.py — Groq API'sinde mevcut modelleri listeler.
Kullanım: python check_models.py (GROQ_API_KEY env değişkeni gerekli)
"""
import os
import sys
from groq import Groq

sys.stdout.reconfigure(encoding="utf-8")

api_key = os.environ.get("GROQ_API_KEY", "")
if not api_key:
    print("HATA: GROQ_API_KEY environment variable bulunamadi.")
    sys.exit(1)

client = Groq(api_key=api_key)
models = client.models.list()
for m in models.data:
    print(m.id)
