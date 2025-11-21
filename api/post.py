import os
import json
import requests
import time
import uuid

SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE"]
BUCKET = os.environ.get("SUPABASE_BUCKET", "images")

def upload_to_supabase(filename, data, content_type):
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"
    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": content_type,
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=data)
    if r.status_code not in (200, 201):
        raise Exception(r.text)
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"

def insert_message(name, text, photo_url):
    url = f"{SUPABASE_URL}/rest/v1/messages"
    headers = {
        "Authorization": f"Bearer {SERVICE_KEY}",
        "apikey": SERVICE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = {
        "name": name,
        "text": text,
        "photo_url": photo_url
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code not in (200, 201):
        raise Exception(r.text)
    return r.json()

def handler(request, response):
    try:
        if request.method != "POST":
            response.status_code = 405
            return response.send("Method Not Allowed")

        form = request.form
        name = (form.get("name") or "").strip()
        text = (form.get("text") or "").strip()

        file = request.files.get("photo")
        photo_url = None

        if file:
            ext = file.filename.split(".")[-1]
            fname = f"{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
            data = file.read()
            photo_url = upload_to_supabase(fname, data, file.content_type)

        rec = insert_message(name or "匿名", text, photo_url)

        return response.send(json.dumps({"ok": True, "data": rec}),
                             headers={"Content-Type":"application/json"})

    except Exception as e:
        response.status_code = 500
        return response.send(json.dumps({"error": str(e)}),
                             headers={"Content-Type":"application/json"})
