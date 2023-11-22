from flask import Flask, render_template, redirect, url_for, session, request
from keycloak import KeycloakOpenID

app = Flask(__name__)
app.secret_key = 'appKeyAuth'



# Configuration Keycloak
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="Digi",
                                 realm_name="Test")

# Page d'accueil
@app.route('/')
def home():
    return render_template('index.html')


# Page de connexion avec Keycloak
@app.route('/login')
def login():
    # Générer l'URL d'authentification avec la redirection
    redirect_uri = request.base_url + '/callback'  # L'URI de redirection est '/login/callback'
    auth_url = keycloak_openid.auth_url(redirect_uri=redirect_uri)
    return redirect(auth_url)

@app.route('/login/callback')
def callback():
    code = request.args.get('code')
    if code:
        try:
            token = keycloak_openid.token(grant_type='authorization_code',code = code, redirect_uri="http://127.0.0.1:5000/login/callback")
            user_info = keycloak_openid.userinfo(token['access_token'])
            # Traitez les informations de l'utilisateur ici
            session['user_info'] = user_info
            return redirect(url_for('dashboard'))
            #return "Utilisateur authentifié: " + str(user_info)
        except Exception as e:
            return "Erreur lors de l'obtention du token: " + str(e) 
    else:
        return "Code d'autorisation non reçu."

# Tableau de bord après l'authentification
@app.route('/dashboard')
def dashboard():
    user_info = session.get('user_info')
    if user_info:
        return f"Welcome {user_info.get('given_name')}"
    return redirect(url_for('login'))

# Déconnexion
@app.route('/logout')
def logout():
    session.pop('user_info', None)
    return redirect(keycloak_openid.logout_url())



if __name__ == '__main__':
    app.run(debug=True)
