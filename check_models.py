import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

if 'GROQ_API_KEY' not in os.environ:
    os.environ['GROQ_API_KEY'] = ''

from groq import Groq
client = Groq(api_key=os.environ['GROQ_API_KEY'])

models = client.models.list()
for m in models.data:
    print(m.id)
