"""
Collections Intelligence - Mock Data Generator
Zolvo Case Study PoC
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

DEBTOR_NAMES = [
    "Anadolu Metal A.Ş.", "Kartal İnşaat Ltd.", "Yıldız Tekstil A.Ş.",
    "Bosphorus Trading Co.", "Ege Gıda San. Ltd.", "İstanbul Lojistik A.Ş.",
    "Marmara Kimya Ltd.", "Akdeniz Tarım A.Ş.", "Karadeniz Enerji Ltd.",
    "Trakya Plastik A.Ş.", "Ankara Makine San.", "Bursa Otomotiv A.Ş.",
    "İzmir Elektronik Ltd.", "Adana Çelik San. A.Ş.", "Konya Mobilya Ltd.",
    "Gaziantep Tekstil A.Ş.", "Mersin Port Trading Ltd.", "Eskişehir Metal A.Ş.",
    "Kayseri Gıda San. Ltd.", "Trabzon Balıkçılık A.Ş.", "Samsun İnşaat Ltd.",
    "Diyarbakır Tarım A.Ş.", "Van Madencilik Ltd.", "Erzurum Enerji A.Ş.",
    "Malatya Kimya San. Ltd.", "Denizli Dokuma A.Ş.", "Muğla Turizm Ltd.",
    "Antalya Resort Dev. A.Ş.", "Bodrum Marine Services Ltd.", "Çanakkale Seramik A.Ş.",
    "Edirne Tarım Ürünleri Ltd.", "Tekirdağ Şarap A.Ş.", "Kocaeli Petrokimya Ltd.",
    "Sakarya Otomotiv San. A.Ş.", "Bolu Kağıt San. Ltd.", "Afyon Mermer A.Ş.",
    "Uşak Deri San. Ltd.", "Manisa Elektronik A.Ş.", "Balıkesir Zeytinlik Ltd.",
    "Çorum Demir San. A.Ş.", "Amasya Gıda Üretim Ltd.", "Kastamonu Orman Ürünleri A.Ş.",
    "Sinop Balıkçılık Ltd.", "Artvin Çay İşleme A.Ş.", "Rize Tarım Ltd.",
    "Giresun Fındık San. A.Ş.", "Ordu Gıda Ltd.", "Tokat Metal San. A.Ş.",
    "Sivas Çimento Ltd.", "Erzincan Maden A.Ş."
]

def generate_mock_debtors(n=50):
    """50 gerçekçi mock borçlu verisi üret — seed sabit, her çağrıda aynı veri"""
    # Fonksiyon içinde seed → Streamlit cache + hot-reload tutarlılığı
    random.seed(42)
    np.random.seed(42)
    records = []
    
    for i in range(n):
        name = DEBTOR_NAMES[i % len(DEBTOR_NAMES)]
        
        # Gerçekçi dağılım için segment belirle
        segment = np.random.choice(
            ['kritik', 'yuksek_risk', 'orta_risk', 'dusuk_risk'],
            p=[0.15, 0.25, 0.35, 0.25]
        )
        
        if segment == 'kritik':
            days_overdue = random.randint(60, 120)
            outstanding_amount = random.uniform(50000, 500000)
            payment_history_score = random.uniform(0, 30)
            days_since_contact = random.randint(20, 60)
            trend = random.choice([-2, -2, -1])  # Kötüleşiyor
            
        elif segment == 'yuksek_risk':
            days_overdue = random.randint(30, 75)
            outstanding_amount = random.uniform(20000, 200000)
            payment_history_score = random.uniform(20, 55)
            days_since_contact = random.randint(10, 30)
            trend = random.choice([-2, -1, -1, 0])
            
        elif segment == 'orta_risk':
            days_overdue = random.randint(10, 45)
            outstanding_amount = random.uniform(5000, 80000)
            payment_history_score = random.uniform(45, 75)
            days_since_contact = random.randint(3, 15)
            trend = random.choice([-1, 0, 0, 1])
            
        else:  # dusuk_risk
            days_overdue = random.randint(0, 20)
            outstanding_amount = random.uniform(1000, 40000)
            payment_history_score = random.uniform(65, 100)
            days_since_contact = random.randint(0, 7)
            trend = random.choice([0, 1, 1, 2])
        
        # Son iletişim tarihi
        last_contact_date = datetime.now() - timedelta(days=days_since_contact)
        
        # Fatura tarihi
        invoice_date = datetime.now() - timedelta(days=days_overdue + random.randint(10, 30))
        
        records.append({
            'debtor_id': f"DBT-{i+1:03d}",
            'debtor_name': name,
            'days_overdue': days_overdue,
            'outstanding_amount': round(outstanding_amount, 2),
            'payment_history_score': round(payment_history_score, 1),
            'days_since_contact': days_since_contact,
            'trend': trend,  # -2: Hızlı kötüleşme, -1: Kötüleşme, 0: Stabil, 1: İyileşme, 2: Hızlı iyileşme
            'last_contact_date': last_contact_date.strftime('%Y-%m-%d'),
            'invoice_date': invoice_date.strftime('%Y-%m-%d'),
            'segment': segment
        })
    
    return pd.DataFrame(records)


if __name__ == "__main__":
    df = generate_mock_debtors()
    print(df.head())
    print(f"\nToplam borçlu: {len(df)}")
    print(f"Segment dağılımı:\n{df['segment'].value_counts()}")
