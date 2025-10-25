# Arquivo: api/tickets.py - Trecho revisado para filtragem por UID
from flask import Flask, request, jsonify
from api._utils.firebase_config import get_db
from api._utils.auth_middleware import required_auth  # Importação do middleware
from datetime import datetime


# ... (código Flask e db) ...

@app.route('/api/tickets', methods=['POST', 'GET'])
# Adiciona o middleware: ele injetará o 'client_uid'
@required_auth
def tickets_handler(client_uid):
    if request.method == 'POST':
        """Cria um novo chamado."""
        # ... (código de validação, igual ao anterior) ...

        new_ticket = {
            # ... (outros campos)
            "client_uid": client_uid,  # ARMAZENA O UID DO CLIENTE QUE CRIOU
            "created_at": datetime.now(),
            # ...
        }

        # ... (código de adição ao Firestore) ...
        # ... (retorna 201) ...

        pass  # placeholder para o código POST

    elif request.method == 'GET':
        """Lista todos os chamados, FILTRANDO APENAS PELO CLIENTE LOGADO."""
        status_filter = request.args.get('status')
        limit = int(request.args.get('limit', 50))

        query = db.collection('tickets')

        # OBRIGA O FILTRO PELO CLIENTE_UID
        query = query.where('client_uid', '==', client_uid)

        if status_filter and status_filter.lower() != 'all':
            query = query.where('status', '==', status_filter)

        query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)

        try:
            tickets = []
            for doc in query.get():
                ticket = doc.to_dict()
                # ... (converte timestamps) ...
                tickets.append({"id": doc.id, **ticket})

            return jsonify(tickets), 200

        except Exception as e:
            return jsonify({"error": f"Erro ao listar chamados: {str(e)}"}), 500

# ... (restante do código) ...