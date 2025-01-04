from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_bootstrap import Bootstrap5
import openai

app = Flask(__name__)
bootstrap = Bootstrap5(app)

import os
openai.api_key = os.getenv("OPENAI_API_KEY")

user_data = {}

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/ask_name', methods=['GET', 'POST'])
def ask_name():
    if request.method == 'POST':
        username = request.form.get('username')
        return redirect(url_for('user', username=username))
    return render_template('ask_name.html')

@app.route('/user/<username>/', methods=['GET', 'POST'])
def user(username):
    user_info = user_data.get(username, {})
    if request.method == 'POST':
        favorite_movie = request.form.get('movie')
        favorite_genre = request.form.get('genre')
        user_data[username] = {
            'favorite_movie': favorite_movie,
            'favorite_genre': favorite_genre
        }
        return render_template('user.html', username=username, user_info=user_data[username], success_message="Preferencias actualizadas!")
    else:
        return render_template('user.html', username=username, user_info=user_info)

@app.route('/chat/<username>/')
def chat(username):
    user_info = user_data.get(username, {})
    return render_template('chat.html', username=username, user_info=user_info)

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    data = request.json
    recommendation_type = data.get('type')
    username = data.get('username')
    user_preferences = data.get('user_preferences', {})

    if not user_preferences:
        return jsonify({"error": "Usuario no encontrado o sin preferencias."}), 404

    favorite_genre = user_preferences.get("favorite_genre", "películas populares")
    favorite_movie = user_preferences.get("favorite_movie", "películas recientes")

    prompt = ""
    if recommendation_type == "preferences":
        prompt = (f"Recomienda una película basada en los gustos de {username}. "
                 f"Su película favorita es {favorite_movie} y le gusta el género {favorite_genre}. "
                 f"Incluye el nombre de la película, una breve reseña y las plataformas donde se puede ver.")
    elif recommendation_type == "trending":
        prompt = ("Recomienda una película que sea tendencia actualmente. "
                 "Incluye el nombre de la película, una breve reseña y las plataformas donde se puede ver.")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Eres un recomendador de películas experto."},
                      {"role": "user", "content": prompt}]
        )
        movie_recommendation = response.choices[0].message['content']
        return jsonify({"recommendation": movie_recommendation})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat_message', methods=['POST'])
def chat_message():
    data = request.json
    user_message = data.get('message')
    if not user_message:
        return jsonify({"error": "Mensaje vacío."}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres Pipoca, un experto en películas y recomendaciones cinematográficas. Habla de forma amigable y divertida."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)