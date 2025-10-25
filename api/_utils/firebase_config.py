# Arquivo: api/_utils/firebase_config.py
import os
import json

import firebase_admin
from firebase_admin import initialize_app, credentials, firestore


# Esta função garante que o Firebase Admin SDK só seja inicializado uma vez
def get_db():
    """
    Inicializa o Firebase Admin SDK usando a chave JSON armazenada
    na variável de ambiente VERCEL/ENV.
    Retorna o cliente do Firestore.
    """
    if not firebase_admin._apps:
        # A chave de serviço JSON completa deve ser armazenada como
        # uma string em uma variável de ambiente do Vercel (ex: FIREBASE_SERVICE_ACCOUNT_KEY).
        try:
            # Tenta carregar a chave de serviço do Vercel
            service_account_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")

            if not service_account_json:
                raise ValueError("Variável de ambiente FIREBASE_SERVICE_ACCOUNT_KEY não encontrada.")

            service_account_info = json.loads(service_account_json)

            cred = credentials.Certificate(service_account_info)
            initialize_app(cred)

        except Exception as e:
            # Em caso de falha (ex: chave mal formatada ou ausente),
            # pode-se tentar uma inicialização default para testes locais se necessário.
            print(f"ERRO DE CONFIGURAÇÃO DO FIREBASE: {e}")
            return None

    return firestore.client()