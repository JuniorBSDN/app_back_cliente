# Arquivo: api/_utils/auth_middleware.py
from functools import wraps
from flask import request, jsonify
from firebase_admin import auth


def required_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # O token deve vir no cabeçalho Authorization: Bearer <token>
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Autenticação requerida"}), 401

        try:
            # Espera um token "Bearer "
            id_token = auth_header.split(' ')[1]

            # Verifica o token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']

            # Passa o UID do cliente para a função do endpoint
            kwargs['client_uid'] = uid

            return f(*args, **kwargs)

        except auth.InvalidIdTokenError:
            return jsonify({"error": "Token inválido ou expirado"}), 401
        except Exception:
            return jsonify({"error": "Formato de token inválido"}), 401

    return decorated_function