from flask import Flask, request, jsonify
from firebase_admin import auth
from api._utils.firebase_config import get_db

app = Flask(__name__)
db = get_db()


@app.route('/api/auth', methods=['POST'])
def login():
    """
    Endpoint de Login. Espera um token JWT do cliente Firebase Auth SDK.
    O Frontend deve enviar { "id_token": "..." }.
    """
    if not request.json or 'id_token' not in request.json:
        return jsonify({"error": "Token de autenticação ausente"}), 400

    id_token = request.json['id_token']

    try:
        # 1. Verifica o ID Token (Admin SDK verifica a validade do token)
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # 2. Busca dados de perfil no Firestore (para obter a role/função)
        user_doc = db.collection('users').document(uid).get()
        if not user_doc.exists:
            # Cria um perfil básico no Firestore se não existir (Opcional)
            db.collection('users').document(uid).set({'role': 'cliente', 'email': decoded_token.get('email', '')})
            user_data = {'role': 'cliente', 'email': decoded_token.get('email', '')}
        else:
            user_data = user_doc.to_dict()

        response_data = {
            "message": "Login bem-sucedido",
            "user": {
                "uid": uid,
                "email": user_data.get('email'),
                "role": user_data.get('role', 'cliente')
            }
        }

        # Retornamos o UID e a role, o token já foi verificado e não precisa ser retornado
        return jsonify(response_data), 200

    except auth.InvalidIdTokenError:
        return jsonify({"error": "Token de autenticação inválido ou expirado"}), 401
    except Exception as e:
        return jsonify({"error": f"Erro no servidor: {str(e)}"}), 500