import qrcode
from PIL import Image
from datetime import datetime, timedelta
from flask import Flask, request, abort

# Initialiser l'application Flask
app = Flask(__name__)

# Fonction pour générer le QR code
def generer_qr_code():
    # Données d'exemple pour la session
    data = ["session_id_exemple"] 

    if data:
        ID_SESSION = data[0]

        # Calculer l'horodatage d'expiration (15 minutes à partir de maintenant)
        expiration_time = datetime.now() + timedelta(minutes=15)
        expiration_timestamp = int(expiration_time.timestamp())

        # Mettre à jour le contenu du QR code pour inclure le timestamp d'expiration en paramètre
        contenu_qr = f"http://127.0.0.1:5000/form?session_id={ID_SESSION}&expires={expiration_timestamp}"

        # Générer le QR code
        qr = qrcode.make(contenu_qr)

        # Sauvegarder l'image du QR code
        qr.save("qr_code.png")
        print("QR code généré avec succès et enregistré sous 'qr_code.png'")

        # Afficher l'image du QR code
        img = Image.open("qr_code.png")
        img.show()  # Cette commande ouvre l'image dans une visionneuse

    else:
        print("Aucune donnée trouvée.")

# Vérifier que le script est exécuté directement et non rechargé en mode debug
if __name__ == "__main__":
    # Appel unique pour générer le QR code avant de lancer l'application Flask
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        generer_qr_code()

    # Exécuter l'application Flask
    app.run(debug=True)

@app.route('/form')
def form():
    # Récupère l'horodatage d'expiration dans l'URL
    expires = request.args.get('expires', type=int)
    current_timestamp = int(datetime.now().timestamp())

    # Vérifier si le QR code a expiré
    if current_timestamp > expires:
        abort(403, description="Le QR code a expiré")
    
    # Si valide, continuer avec le traitement
    return "QR code valide. Continuer le traitement du formulaire."
