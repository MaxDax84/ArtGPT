from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os
import base64
from google.cloud import vision

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
conversazione = []

# Funzione di riconoscimento tramite Google Cloud Vision API
def riconosci_immagine_base64(base64_string):
    try:
        vision_client = vision.ImageAnnotatorClient()

        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        image = vision.Image(content=base64.b64decode(base64_string))
        response = vision_client.web_detection(image=image)
        web_detection = response.web_detection

        if web_detection.web_entities:
            migliori = sorted(web_detection.web_entities, key=lambda e: e.score, reverse=True)
            for entity in migliori:
                if entity.description:
                    return f"L'immagine sembra rappresentare: {entity.description}"
        return "L'immagine non ha una corrispondenza chiara secondo il database di Google."

    except Exception as e:
        return f"Errore da Google Vision: {str(e)}"

@app.route("/")
def home():
    return send_from_directory('', 'index.html')

@app.route("/chiedi", methods=["POST"])
def chiedi():
    global conversazione
    try:
        data = request.get_json()

        if data.get("reset"):
            conversazione = []
            return jsonify({"risposta": "🔄 Conversazione resettata. ArtGPT è pronto per una nuova discussione sull'arte."})

        domanda = data.get("domanda", "").strip()
        if not domanda:
            return jsonify({"risposta": "Per favore, scrivi una domanda."})

        prompt_iniziale = {
            "role": "system",
            "content": (
                "Sei ArtGPT, un esperto di storia dell’arte, museologia, critica e tecniche artistiche. "
                "Rispondi con precisione e creatività a domande sull'arte. "
                "Se la domanda è generica, prova a interpretarla in chiave artistica o filosofica."
            )
        }

        conversazione.append({"role": "user", "content": domanda})
        messaggi = [prompt_iniziale] + conversazione

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messaggi,
            max_tokens=700,
            temperature=0.7
        )

        risposta = response.choices[0].message.content.strip()
        conversazione.append({"role": "assistant", "content": risposta})

        return jsonify({"risposta": risposta})

    except Exception as e:
        return jsonify({"risposta": f"Errore: {str(e)}"})

@app.route("/analizza", methods=["POST"])
def analizza():
    try:
        data = request.get_json()
        image_data = data.get("imageData", "")

        if not image_data.startswith("data:image"):
            return jsonify({"risposta": "Formato immagine non valido."})

        riconoscimento = riconosci_immagine_base64(image_data)

        prompt = {
            "role": "system",
            "content": (
                "Sei un assistente esperto d’arte. Un utente ti ha inviato un'immagine. "
                "Commenta lo stile pittorico, l’epoca, i tratti visivi, eventuali influenze e possibili autori. "
                "Sottolinea che l’analisi si basa su una rappresentazione visiva. "
                "Se disponibile, considera anche il titolo identificato tramite rete neurale."
            )
        }

        descrizione = {
            "role": "user",
            "content": f"L'utente ha caricato un'immagine. Il sistema ha identificato: {riconoscimento}. "
                       f"Commenta e analizza quest'opera da un punto di vista artistico."
        }

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[prompt, descrizione],
            max_tokens=600,
            temperature=0.8
        )

        risposta = response.choices[0].message.content.strip()
        return jsonify({"risposta": risposta})

    except Exception as e:
        return jsonify({"risposta": f"Errore durante l'analisi dell'immagine: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
