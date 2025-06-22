from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
            return jsonify({"risposta": "🔄 Conversazione resettata. ArtGPT è pronto per una nuova discussione sull'arte."})

        domanda = data.get("domanda", "").strip()
        if not domanda:
            return jsonify({"risposta": "Per favore, scrivi una domanda."})

        # Prompt dinamico: lascia decidere al modello se la domanda è attinente all'arte
        prompt_iniziale = {
            "role": "system",
            "content": (
                "Sei ArtGPT, un esperto di storia dell’arte, museologia, critica e tecniche artistiche. "
                "Il tuo compito è rispondere con serietà, precisione e autorevolezza a domande attinenti all'arte. "
                "Se la domanda non è direttamente legata all'arte, puoi gentilmente dirlo, ma prova comunque a fornire "
                "una risposta in chiave artistica, filosofica o creativa, coerente con il tuo stile. "
                "Risposte sempre ben strutturate in paragrafi ordinati, anche con elenchi se utile. "
                "Tieni conto delle domande precedenti per mantenere il contesto e la coerenza nella conversazione."
            )
        }

        conversazione.append({"role": "user", "content": domanda})
        messaggi = [prompt_iniziale] + conversazione

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messaggi,
            max_tokens=600,
            temperature=0.7
        )

        risposta = response.choices[0].message.content.strip()
        conversazione.append({"role": "assistant", "content": risposta})

        return jsonify({"risposta": risposta})

    except Exception as e:
        return jsonify({"risposta": f"Errore: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
