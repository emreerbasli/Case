"""
Collections Intelligence - Risk Scoring Engine
Zolvo Case Study PoC

Risk Formülü (Belgedeki ağırlıklara göre):
- days_overdue      : %35
- outstanding_amount: %25
- payment_history   : %20 (ters orantılı)
- days_since_contact: %20
- trend             : katkı değişken (±bonus)
"""

import pandas as pd


def normalize_overdue(days: float, max_days: float = 120) -> float:
    """Gecikme gününü 0-100 arasına normalize et"""
    return min(days / max_days, 1.0) * 100


def normalize_amount(amount: float, max_amount: float = 500000) -> float:
    """Açık tutarı 0-100 arasına normalize et"""
    return min(amount / max_amount, 1.0) * 100


def normalize_payment_history(score: float) -> float:
    """Ödeme geçmişini ters orantılı risk skoruna çevir (yüksek skor = düşük risk)"""
    return 100 - score


def normalize_contact_gap(days: float, max_days: float = 60) -> float:
    """Son iletişimden geçen günü 0-100 arasına normalize et"""
    return min(days / max_days, 1.0) * 100


def calculate_trend_bonus(trend: int) -> float:
    """
    Trend katkısı:
    -2: Hızlı kötüleşme → +15 puan
    -1: Kötüleşme       → +7 puan
     0: Stabil          →  0 puan
     1: İyileşme        → -5 puan
     2: Hızlı iyileşme  → -10 puan
    """
    bonus_map = {-2: 15, -1: 7, 0: 0, 1: -5, 2: -10}
    return bonus_map.get(trend, 0)


def calculate_sector_risk(sector: str) -> float:
    """Sektör bazlı risk skoru (100 en riskli)"""
    sector_map = {
        "İnşaat": 100,
        "Perakende": 80,
        "Lojistik": 60,
        "Üretim": 40,
        "Teknoloji": 20,
        "Sağlık": 10
    }
    return sector_map.get(sector, 50)


def calculate_credit_risk(rating: str) -> float:
    """Kredi notuna göre risk skoru (100 en riskli)"""
    rating_map = {
        "A": 10,
        "B": 35,
        "C": 70,
        "D": 100
    }
    return rating_map.get(rating, 50)


def calculate_risk_score(row: pd.Series) -> dict:
    """
    Her borçlu için açıklanabilir risk skoru hesapla.
    Yeni Formül:
    - Gecikme (%30)
    - Tutar (%20)
    - Geçmiş (%15)
    - İletişim (%10)
    - Sektör Riski (%15)
    - Kredi Notu (%10)
    """
    # Normalize edilmiş bileşenler
    overdue_norm = normalize_overdue(row["days_overdue"])
    amount_norm = normalize_amount(row["outstanding_amount"])
    history_risk = normalize_payment_history(row["payment_history_score"])
    contact_norm = normalize_contact_gap(row["days_since_contact"])
    sector_risk = calculate_sector_risk(row["sector"])
    credit_risk = calculate_credit_risk(row["credit_rating"])
    trend_bonus = calculate_trend_bonus(row["trend"])

    # Yeni Ağırlıklı formül
    base_score = (
        overdue_norm * 0.30
        + amount_norm * 0.20
        + history_risk * 0.15
        + contact_norm * 0.10
        + sector_risk * 0.15
        + credit_risk * 0.10
    )

    # Trend bonusu ekle ve 0-100 arasında sınırla
    final_score = max(0, min(100, base_score + trend_bonus))

    breakdown = {
        "overdue_component": round(overdue_norm * 0.30, 2),
        "amount_component": round(amount_norm * 0.20, 2),
        "history_component": round(history_risk * 0.15, 2),
        "contact_component": round(contact_norm * 0.10, 2),
        "sector_component": round(sector_risk * 0.15, 2),
        "credit_component": round(credit_risk * 0.10, 2),
        "trend_bonus": round(trend_bonus, 2),
        "base_score": round(base_score, 2),
    }

    return {"risk_score": round(final_score, 1), "score_breakdown": breakdown}


def get_action(risk_score: float) -> str:
    """
    Risk skoruna göre aksiyon belirle:
    80-100 → Hemen Ara (Kritik)
    60-79  → E-posta At
    40-59  → Takipte Tut
    0-39   → Bekle
    """
    if risk_score >= 80:
        return "🔴 Hemen Ara"
    elif risk_score >= 60:
        return "🟠 E-posta At"
    elif risk_score >= 40:
        return "🟡 Takipte Tut"
    else:
        return "🟢 Bekle"


def get_action_en(risk_score: float) -> str:
    """English action label"""
    if risk_score >= 80:
        return "Call Immediately"
    elif risk_score >= 60:
        return "Send Email"
    elif risk_score >= 40:
        return "Monitor"
    else:
        return "Wait"


def get_action_color(risk_score: float) -> str:
    """Streamlit renk kodu"""
    if risk_score >= 80:
        return "red"
    elif risk_score >= 60:
        return "orange"
    elif risk_score >= 40:
        return "yellow"
    else:
        return "green"


def get_trend_label(trend: int) -> str:
    """Trend etiketleri"""
    trend_map = {
        -2: "📉 Hızlı Kötüleşiyor",
        -1: "↘️ Kötüleşiyor",
        0: "➡️ Stabil",
        1: "↗️ İyileşiyor",
        2: "📈 Hızlı İyileşiyor",
    }
    return trend_map.get(trend, "➡️ Stabil")


def score_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    """Tüm portföyü skorla"""
    results = []

    for _, row in df.iterrows():
        scoring = calculate_risk_score(row)
        risk_score = scoring["risk_score"]
        breakdown = scoring["score_breakdown"]

        result = {
            "debtor_id": row["debtor_id"],
            "debtor_name": row["debtor_name"],
            "sector": row["sector"],
            "credit_rating": row["credit_rating"],
            "invoice_count": row["invoice_count"],
            "historical_delays": row["historical_delays"],
            "days_overdue": row["days_overdue"],
            "outstanding_amount": row["outstanding_amount"],
            "payment_history_score": row["payment_history_score"],
            "days_since_contact": row["days_since_contact"],
            "trend": row["trend"],
            "trend_label": get_trend_label(row["trend"]),
            "last_contact_date": row["last_contact_date"],
            "invoice_date": row["invoice_date"],
            "risk_score": risk_score,
            "action": get_action(risk_score),
            "action_en": get_action_en(risk_score),
            "action_color": get_action_color(risk_score),
            # Skor bileşenleri (açıklanabilirlik için)
            "score_overdue": breakdown["overdue_component"],
            "score_amount": breakdown["amount_component"],
            "score_history": breakdown["history_component"],
            "score_contact": breakdown["contact_component"],
            "score_sector": breakdown["sector_component"],
            "score_credit": breakdown["credit_component"],
            "score_trend": breakdown["trend_bonus"],
        }
        results.append(result)

    scored_df = pd.DataFrame(results)

    # Risk skoruna göre sırala (en yüksek önce)
    scored_df = scored_df.sort_values("risk_score", ascending=False).reset_index(
        drop=True
    )
    scored_df.index += 1  # 1'den başlat

    return scored_df


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")

    from data_generator import generate_mock_debtors

    df = generate_mock_debtors()
    scored = score_portfolio(df)

    # Emoji'leri strip et (terminal uyumluluğu için)
    display = (
        scored[
            [
                "debtor_name",
                "risk_score",
                "action_en",
                "days_overdue",
                "outstanding_amount",
            ]
        ]
        .head(10)
        .copy()
    )

    print("=== TOP 10 HIGH RISK DEBTORS ===")
    print(display.to_string())

    print("\n=== ACTION DISTRIBUTION ===")
    print(scored["action_en"].value_counts())
