from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

# Inizializza il client OpenAI con la chiave API dalla variabile d'ambiente
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Memoria temporanea della conversazione per mantenere il contesto
conversazione = []

@app.route("/")
def home():
    return send_from_directory('', 'index.html')

@app.route("/chiedi", methods=["POST"])
def chiedi():
    global conversazione
    try:
        data = request.get_json()

        # Se richiesto il reset della conversazione
        if data.get("reset"):
            conversazione = []
            return jsonify({"risposta": "🔄 Conversazione resettata. ArtGPT è pronto per una nuova discussione sull'arte."})

        domanda = data.get("domanda")
        if not domanda:
            return jsonify({"risposta": "Per favore, scrivi una domanda."})

        # Aggiunge la domanda corrente alla cronologia
        conversazione.append({"role": "user", "content": domanda})

        # Prompt di sistema per istruire ArtGPT
        prompt_iniziale = {
            "role": "system",
            "content": (
                "Sei ArtGPT, un esperto di storia dell’arte, museologia, critica e tecniche artistiche. "
                "Rispondi con serietà, precisione e autorevolezza solo in relazione all'arte. "
                "Ogni risposta deve essere coerente con il contesto delle domande precedenti. "
                "Collega le nuove risposte a quelle già fornite, quando possibile. "
                "Se una domanda è ambigua, chiedi chiarimenti, ma sempre restando nel campo artistico. "
                "Formato: struttura la risposta con paragrafi leggibili e ordinati, dividi i concetti "
                "e usa uno stile chiaro e professionale."
            )
        }

        messaggi = [prompt_iniziale] + conversazione

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messaggi,
            max_tokens=500,
            temperature=0.7
        )

        risposta = response.choices[0].message.content.strip()
        conversazione.append({"role": "assistant", "content": risposta})

        return jsonify({"risposta": risposta})

    except Exception as e:
        return jsonify({"risposta": f"Errore: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
