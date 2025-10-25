# Arquivo: api/dashboard.py
from flask import Flask, jsonify
from api._utils.firebase_config import get_db

app = Flask(__name__)
db = get_db()


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_summary():
    """Obtém dados de resumo para o dashboard (GET /api/dashboard)."""
    try:
        tickets_ref = db.collection('tickets')

        # 1. Obter contagem total
        total_tickets = len(tickets_ref.get())

        # 2. Obter contagem de status específicos (Aberto, Fechado, etc.)
        abertos = len(tickets_ref.where('status', '==', 'Aberto').get())
        concluidos = len(tickets_ref.where('status', '==', 'Concluído').get())
        pendentes = len(tickets_ref.where('status', '==', 'Pendente').get())

        # 3. Dados de exemplo para o gráfico (Em produção, você faria uma query agregada por mês/ano)
        performance_data = {
            "labels": ["Set", "Out", "Nov", "Dez", "Jan"],
            "data": [28, 32, 35, 30, 25]  # Exemplo de chamados concluídos por mês
        }

        summary = {
            "total_tickets": total_tickets,
            "open_tickets": abertos,
            "closed_tickets": concluidos,
            "pending_tickets": pendentes,
            "chart_performance": performance_data
        }

        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao carregar dashboard: {str(e)}"}), 500


# Vercel Handler
if __name__ == '__main__':
    app.run(debug=True)