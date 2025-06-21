from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Conversazione in memoria temporanea
conversazione = []

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
            return jsonify({"risposta": "🔄 Conversazione resettata. Sentiti libero di iniziare una nuova domanda artistica!"})

        domanda = data.get("domanda")
        if not domanda:
            return jsonify({"risposta": "Per favore, scrivi una domanda."})

        conversazione.append({"role": "user", "content": domanda})

        # Prompt iniziale per impostare il tono
        prompt_iniziale = {
            "role": "system",
            "content": (
                "Sei un esperto d'arte di altissimo livello. Rispondi a qualsiasi domanda solo in relazione all'arte, "
                "con tono serio, professionale e preciso. Anche se la domanda sembra generale, riportala sempre all'arte. "
                "FORMATTAZIONE: usa paragrafi e chiarezza. CONTINUITÀ: collega le risposte al contesto precedente."
            )
        }

        messaggi = [prompt_iniziale] + conversazione

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messaggi,
            max_tokens=400,
            temperature=0.7
        )

        risposta = response.choices[0].message.content.strip()
        conversazione.append({"role": "assistant", "content": risposta})

        return jsonify({"risposta": risposta})

    except Exception as e:
        return jsonify({"risposta": f"Errore: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
