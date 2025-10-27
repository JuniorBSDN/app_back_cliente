# api/back_informatica.py
# Flask API inicial para Back Informática (integração com Firestore)
# Rotas:
#  POST /api/login         -> {"username","password"} -> {user data + empresa_id, token(simulado)}
#  POST /api/chamados      -> cria chamado (body JSON)
#  GET  /api/chamados      -> lista chamados (query ?empresa_id=... optional)
#  GET  /api/relatorios    -> retorna resumo financeiro básico por empresa (?empresa_id=...)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, datetime
import traceback

# Firestore
import firebase_admin
from firebase_admin import credentials, firestore

# ---------- Config / Init ----------
app = Flask(__name__)
CORS(app)

FIREBASE_SERVICE_ACCOUNT = os.environ.get('FIREBASE_SERVICE_ACCOUNT')  # JSON string
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')  # optional for verification

if not FIREBASE_SERVICE_ACCOUNT:
    # If service account not provided, app will still start but Firestore operations will fail with clear error.
    print("WARNING: FIREBASE_SERVICE_ACCOUNT not set. Firestore won't initialize until provided.")

db = None
try:
    if FIREBASE_SERVICE_ACCOUNT:
        sa_info = json.loads(FIREBASE_SERVICE_ACCOUNT)
        cred = credentials.Certificate(sa_info)
        firebase_admin.initialize_app(cred, {
            'projectId': sa_info.get('project_id') or FIREBASE_PROJECT_ID
        })
        db = firestore.client()
        print("Firestore initialized.")
except Exception as e:
    print("Error initializing Firestore:", e)
    traceback.print_exc()

# ---------- Helpers ----------
def error_response(message, code=400):
    return jsonify({"ok": False, "error": message}), code

def now_iso():
    return datetime.datetime.utcnow().isoformat() + 'Z'

# ---------- Routes ----------
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"ok": True, "time": now_iso(), "msg": "Back Informatica API alive"})

# POST /api/login
@app.route('/api/login', methods=['POST'])
def login():
    """
    Body (JSON): { "username": "...", "password": "..." }
    Returns user data with empresa_id if credentials match (simple validation).
    NOTE: Passwords in Firestore should be hashed in production.
    """
    try:
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return error_response("username and password required", 400)

        if db is None:
            return error_response("Firestore not initialized. Set FIREBASE_SERVICE_ACCOUNT env var.", 500)

        users_ref = db.collection('usuarios')
        q = users_ref.where('username', '==', username).limit(1).get()
        if not q:
            return error_response("Usuário não encontrado", 404)

        user_doc = q[0]
        user = user_doc.to_dict()
        # Simple password check (INSECURE). Replace with hashed passwords in prod.
        if 'password' not in user or user.get('password') != password:
            return error_response("Senha incorreta", 401)

        if user.get('status') == 'blocked':
            return jsonify({"ok": False, "error": "Usuário bloqueado"}), 403

        # Create a simple session token (simulado). Use JWT in production.
        token = f"simulated-token-{user_doc.id}-{int(datetime.datetime.utcnow().timestamp())}"

        result = {
            "ok": True,
            "user": {
                "id": user_doc.id,
                "name": user.get('name'),
                "username": user.get('username'),
                "role": user.get('role', 'user'),
                "empresa_id": user.get('empresa_id')
            },
            "token": token
        }
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return error_response(str(e), 500)

# POST /api/chamados
@app.route('/api/chamados', methods=['POST'])
def create_chamado():
    """
    Creates a chamado.
    Expected JSON body: {
      "empresa_id": "empresa_001",
      "requester": "...",
      "telefone": "...",
      "secretaria": "...",
      "setor": "...",
      "endereco": "...",
      "equipamento": "...",
      "marca": "...",
      "serie": "...",
      "condicao": "...",
      "urgente": true/false,
      "descricao": "..."
    }
    """
    try:
        payload = request.get_json(force=True)
        if not payload:
            return error_response("JSON body required", 400)

        if db is None:
            return error_response("Firestore not initialized", 500)

        empresa_id = payload.get('empresa_id')
        if not empresa_id:
            return error_response("empresa_id is required in payload", 400)

        chamados_ref = db.collection('chamados')
        novo = {
            "empresa_id": empresa_id,
            "requester": payload.get('requester'),
            "telefone": payload.get('telefone'),
            "secretaria": payload.get('secretaria'),
            "setor": payload.get('setor'),
            "endereco": payload.get('endereco'),
            "equipamento": payload.get('equipamento'),
            "marca": payload.get('marca'),
            "serie": payload.get('serie'),
            "condicao": payload.get('condicao'),
            "urgente": bool(payload.get('urgente', False)),
            "descricao": payload.get('descricao'),
            "status": payload.get('status', 'Aguardando Atendimento'),
            "created_at": firestore.SERVER_TIMESTAMP
        }

        doc_ref = chamados_ref.add(novo)  # (doc_ref, write_time)
        created_id = doc_ref[1].time if False else None  # not used, but keeping form

        # Return created document minimal info
        return jsonify({"ok": True, "chamado": { **novo, "id": doc_ref[0].id }}), 201
    except Exception as e:
        traceback.print_exc()
        return error_response(str(e), 500)

# GET /api/chamados
@app.route('/api/chamados', methods=['GET'])
def list_chamados():
    """
    Query params:
      - empresa_id (optional) : filter by empresa_id
      - status (optional) : filter by status
      - limit (optional): limit results
    """
    try:
        if db is None:
            return error_response("Firestore not initialized", 500)

        empresa_id = request.args.get('empresa_id')
        status = request.args.get('status')
        limit = int(request.args.get('limit') or 200)

        chamados_ref = db.collection('chamados')
        query = chamados_ref.order_by('created_at', direction=firestore.Query.DESCENDING)

        if empresa_id:
            query = query.where('empresa_id', '==', empresa_id)
        if status:
            query = query.where('status', '==', status)

        docs = query.limit(limit).stream()
        result = []
        for d in docs:
            data = d.to_dict()
            data['id'] = d.id
            # Convert Firestore timestamps to ISO string if present
            if isinstance(data.get('created_at'), firestore.SERVER_TIMESTAMP.__class__):
                # leave as is; client should handle
                pass
            result.append(data)

        return jsonify({"ok": True, "count": len(result), "chamados": result})
    except Exception as e:
        traceback.print_exc()
        return error_response(str(e), 500)

# GET /api/relatorios
@app.route('/api/relatorios', methods=['GET'])
def relatorios():
    """
    Simple report aggregation by empresa_id.
    Query params:
     - empresa_id (required)
    Returns totals: total_chamados, pendentes, concluidos, horas_estimada (if available) etc.
    """
    try:
        if db is None:
            return error_response("Firestore not initialized", 500)

        empresa_id = request.args.get('empresa_id')
        if not empresa_id:
            return error_response("empresa_id query param required", 400)

        chamados_ref = db.collection('chamados')
        all_docs = chamados_ref.where('empresa_id', '==', empresa_id).stream()

        total = 0
        pendentes = 0
        concluidos = 0
        urgentes = 0

        for d in all_docs:
            total += 1
            doc = d.to_dict()
            st = doc.get('status', '').lower()
            if 'concl' in st or st == 'concluído' or st == 'concluido':
                concluidos += 1
            elif 'pend' in st or st == 'pendente':
                pendentes += 1
            if doc.get('urgente'):
                urgentes += 1

        return jsonify({
            "ok": True,
            "empresa_id": empresa_id,
            "total_chamados": total,
            "pendentes": pendentes,
            "concluidos": concluidos,
            "urgentes": urgentes
        })
    except Exception as e:
        traceback.print_exc()
        return error_response(str(e), 500)

# ---------- Run ----------
# On Vercel, the WSGI entrypoint is this file. For local testing:
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
