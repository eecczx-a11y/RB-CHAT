import os
import json
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
ANON = os.environ["SUPABASE_ANON"]

def handler(request, response):
    try:
        url = f"{SUPABASE_URL}/rest/v1/messages?select=*&order=created_at.desc"
        headers = {
            "apikey": ANON,
            "Authorization": f"Bearer {ANON}"
        }
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return response.send(r.text, headers={"Content-Type":"application/json"})

    except Exception as e:
        response.status_code = 500
        return response.send(json.dumps({"error": str(e)}),
                             headers={"Content-Type":"application/json"})
