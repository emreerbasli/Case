"""
Collections Intelligence - Groq LLM Explanation Engine
Zolvo Case Study PoC

Her borçlu için açıklanabilir karar metni üretir.
Model: Llama 3.3 70B via Groq API (ücretsiz tier)

NOT: LLM karar VERMEZ — açıklar. Bu kritik ayrımdır.
"""

import os
import time
import pandas as pd
from groq import Groq

# Proje API model
_DEFAULT_MODEL = "llama-3.3-70b-versatile"



def get_groq_client():
    """Groq client'ı başlat"""
    # API key Cloudflare üzerinde saklanıyor, proxy URL üzerinden erişiyoruz
    return Groq(
        api_key="secured-by-cloudflare",
        base_url="https://zolvo-groq-proxy.emrezeynoel.workers.dev"
    )


def build_explanation_prompt(row: pd.Series, language: str = "tr") -> str:
    """
    Borçlu verilerinden LLM prompt'u oluştur.
    LLM sadece açıklar, karar vermez.
    """
    trend_map = {
        -2: "hızla kötüleşiyor",
        -1: "kötüleşiyor",
        0: "stabil",
        1: "iyileşiyor",
        2: "hızla iyileşiyor",
    }
    trend_text = trend_map.get(row["trend"], "stabil")

    action_clean = (
        row["action"]
        .replace("🔴 ", "")
        .replace("🟠 ", "")
        .replace("🟡 ", "")
        .replace("🟢 ", "")
    )

    if language == "tr":
        prompt = f"""Bir Collections Intelligence sistemisin. Aşağıdaki borçlu için, neden bu aksiyonun önerildiğini 1-2 cümleyle açıkla.
KURAL: Sadece açıkla, karar VERME. İnsan yönetici nihai kararı verir.
Ton: Profesyonel, net, finansal.

Borçlu: {row['debtor_name']}
Risk Skoru: {row['risk_score']}/100
Önerilen Aksiyon: {action_clean}
Gecikme Günü: {row['days_overdue']} gün
Açık Tutar: {row['outstanding_amount']:,.0f} USD
Ödeme Geçmiş Skoru: {row['payment_history_score']}/100
Son İletişimden Bu Yana: {row['days_since_contact']} gün
Gecikme Trendi: {trend_text}

Tek paragraf, maksimum 2 cümle. Türkçe yaz."""
    else:
        prompt = f"""You are a Collections Intelligence system. Explain in 1-2 sentences why this action is recommended for the following debtor.
RULE: Only explain, do NOT make the decision. The human manager makes the final call.
Tone: Professional, concise, financial.

Debtor: {row['debtor_name']}
Risk Score: {row['risk_score']}/100
Recommended Action: {action_clean}
Days Overdue: {row['days_overdue']} days
Outstanding Amount: {row['outstanding_amount']:,.0f} USD
Payment History Score: {row['payment_history_score']}/100
Days Since Last Contact: {row['days_since_contact']} days
Trend: {trend_text}

Single paragraph, max 2 sentences. Write in English."""

    return prompt


def generate_explanation(
    client: Groq, row: pd.Series, language: str = "tr", model: str = _DEFAULT_MODEL
) -> str:
    """Tek bir borçlu için Groq API'si ile açıklama üret"""

    prompt = build_explanation_prompt(row, language)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Sen bir fintech AI sistemisin. Kısa, net ve açıklanabilir kararlar üretirsin. Asla spekülatif veya kesin tahmin yapmazsın.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.3,  # Tutarlı çıktı için düşük temperature
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[API Hatası: {str(e)[:80]}]"


def generate_all_explanations(
    df: pd.DataFrame, language: str = "tr", max_rows: int = None, delay: float = 0.3
) -> pd.DataFrame:
    """
    Tüm portföy için açıklamalar üret.
    Rate limit aşımını önlemek için delay ekle.

    Args:
        df: Skorlanmış borçlu DataFrame'i
        language: 'tr' veya 'en'
        max_rows: Sadece ilk N borçluyu işle (test için)
        delay: API çağrıları arası bekleme (saniye)
    """
    client = get_groq_client()

    if max_rows:
        df = df.head(max_rows)

    explanations = []

    for idx, row in df.iterrows():
        explanation = generate_explanation(client, row, language)
        explanations.append(explanation)

        # Rate limit koruması
        if delay > 0:
            time.sleep(delay)

    df = df.copy()
    col_name = f"explanation_{language}"
    df[col_name] = explanations

    return df


def get_single_explanation(row: pd.Series, language: str = "tr") -> str:
    """Dashboard'da tek borçlu için on-demand açıklama"""
    try:
        client = get_groq_client()
        return generate_explanation(client, row, language)
    except Exception as e:
        return f"Açıklama üretilemiyor: {str(e)[:100]}"


if __name__ == "__main__":
    # Test: İlk 3 borçlu için açıklama üret
    from data_generator import generate_mock_debtors
    from scoring_engine import score_portfolio

    df = generate_mock_debtors()
    scored = score_portfolio(df)

    print("İlk 3 yüksek riskli borçlu için açıklama üretiliyor...")
    result = generate_all_explanations(scored, language="tr", max_rows=3)

    for _, row in result.iterrows():
        print(f"\n{'='*60}")
        print(f"Borçlu: {row['debtor_name']}")
        print(f"Risk Skoru: {row['risk_score']} | Aksiyon: {row['action']}")
        print(f"Açıklama: {row['explanation_tr']}")
