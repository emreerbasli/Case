import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

if 'GROQ_API_KEY' not in os.environ:
    os.environ['GROQ_API_KEY'] = ''

from data_generator import generate_mock_debtors
from scoring_engine import score_portfolio
from llm_engine import get_single_explanation

df = generate_mock_debtors()
scored = score_portfolio(df)

# En yuksek riskli ilk 3 borclu icin test
for i in range(3):
    row = scored.iloc[i]
    print(f"\n{'='*60}")
    print(f"Borclu: {row['debtor_name']}")
    print(f"Risk Skoru: {row['risk_score']} | Aksiyon: {row['action_en']}")
    print(f"Gecikme: {row['days_overdue']} gun | Acik Tutar: ${row['outstanding_amount']:,.0f}")
    print()
    print("TR: ", get_single_explanation(row, 'tr'))
    print()
    print("EN: ", get_single_explanation(row, 'en'))
