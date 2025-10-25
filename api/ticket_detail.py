# Arquivo: api/ticket_detail.py
from flask import Flask, request, jsonify
from api._utils.firebase_config import get_db
from datetime import datetime

# Usamos um prefixo 'detail' para distinguir, e um roteamento no vercel.json
app = Flask(__name__)
db = get_db()


# A rota real será /api/tickets/[id] (no vercel.json)
@app.route('/api/tickets/<ticket_id>', methods=['GET', 'PATCH'])
def ticket_detail_handler(ticket_id):
    ticket_ref = db.collection('tickets').document(ticket_id)

    if request.method == 'GET':
        """Obtém os detalhes de um chamado (GET /api/tickets/<id>)."""
        try:
            doc = ticket_ref.get()
            if not doc.exists:
                return jsonify({"error": "Chamado não encontrado"}), 404

            ticket = doc.to_dict()
            # Converte timestamps para string
            ticket['created_at'] = ticket['created_at'].isoformat() if ticket.get('created_at') else None
            ticket['updated_at'] = ticket['updated_at'].isoformat() if ticket.get('updated_at') else None

            return jsonify({"id": doc.id, **ticket}), 200

        except Exception as e:
            return jsonify({"error": f"Erro ao obter detalhes: {str(e)}"}), 500

    elif request.method == 'PATCH':
        """Atualiza o status/solução de um chamado (PATCH /api/tickets/<id>)."""
        data = request.json
        if not data:
            return jsonify({"error": "Dados de atualização ausentes"}), 400

        update_data = {}
        history_entry = {"timestamp": datetime.now()}

        # Campos de atualização possíveis (ex: fechar chamado)
        if 'new_status' in data:
            update_data['status'] = data['new_status']
            history_entry['status'] = data['new_status']
        if 'solution' in data:
            update_data['solution'] = data['solution']
            history_entry['note'] = data['solution']
        if 'cost' in data:
            update_data['cost'] = data['cost']  # Valor total do RAT

        if not update_data:
            return jsonify({"message": "Nenhum campo para atualização fornecido"}), 200

        update_data['updated_at'] = datetime.now()

        try:
            # 1. Atualiza o documento principal
            ticket_ref.update(update_data)

            # 2. Adiciona ao histórico (ArrayUnion no Firestore)
            if 'note' in history_entry or 'status' in history_entry:
                ticket_ref.update({
                    "history": firestore.ArrayUnion(history_entry)
                })

            return jsonify({
                "message": "Chamado atualizado com sucesso",
                "ticket_id": ticket_id
            }), 200

        except Exception as e:
            return jsonify({"error": f"Erro ao atualizar chamado: {str(e)}"}), 500


# Vercel Handler
if __name__ == '__main__':
    app.run(debug=True)