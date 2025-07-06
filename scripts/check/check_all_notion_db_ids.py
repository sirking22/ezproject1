import os
from dotenv import load_dotenv

load_dotenv()

print("=== Все Notion Database ID из окружения ===")
for k in sorted(os.environ):
    if "NOTION" in k and k.endswith("_DB_ID"):
        print(f"{k} = {os.environ[k]}") 