from flask import Flask, render_template, request

app = Flask(__name__)

# Page d'accueil avec le formulaire
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        return f"<h2>Bonjour, {prenom} {nom}!</h2>"
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
