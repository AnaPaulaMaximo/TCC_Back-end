from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mysql.connector
from mysql.connector import IntegrityError
import google.generativeai as genai
from dotenv import load_dotenv
import os
from uuid import uuid4
import json
import random

# --- Configurações Iniciais ---
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Conexão MySQL ---
# (Certifique-se que seu arquivo config.py está correto)
from config import conn, cursor

# --- Configuração Google GenAI ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-pro" 

# --- FUNÇÕES AUXILIARES ---

def carregar_dados_json(nome_arquivo):
    """Carrega dados de um arquivo JSON local."""
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_user_plan(id_aluno):
    """Busca o plano do usuário no banco de dados."""
    try:
        cursor.execute('SELECT plano FROM Aluno WHERE id_aluno = %s', (id_aluno,))
        resultado = cursor.fetchone()
        if resultado and resultado.get('plano'):
            return resultado['plano']
    except Exception as e:
        print(f"Erro ao buscar plano do usuário: {e}")
    return 'freemium' # Retorna 'freemium' como padrão em caso de erro

# ===================================
# Rotas de Autenticação e Usuário
# (Mantidas do projeto original)
# ===================================
@app.route('/')
def index():
    return 'API ON', 200

@app.route('/login', methods=['POST'])
def login():
    # As duas linhas abaixo estavam faltando
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    cursor.execute('SELECT id_alufrom flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mysql.connector
from mysql.connector import IntegrityError
import google.generativeai as genai
from dotenv import load_dotenv
import os
from uuid import uuid4
import json
import random

# --- Configurações Iniciais ---
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Conexão MySQL ---
from config import conn, cursor

# --- Configuração Google GenAI ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("ERRO: A variável de ambiente GOOGLE_API_KEY não está definida.")
else:
    genai.configure(api_key=API_KEY)

# CORREÇÃO: Voltando ao nome do modelo original que funcionava.
MODEL_NAME = "gemini-1.5-flash" 

# --- FUNÇÕES AUXILIARES ---

def carregar_dados_json(nome_arquivo):
    """Carrega dados de um arquivo JSON local."""
    try:
        # Garante que o caminho para o JSON seja relativo ao arquivo app.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, nome_arquivo)
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"AVISO: Não foi possível carregar o arquivo {nome_arquivo}.")
        return []

def get_user_plan(id_aluno):
    """Busca o plano do usuário no banco de dados."""
    try:
        cursor.execute('SELECT plano FROM Aluno WHERE id_aluno = %s', (id_aluno,))
        resultado = cursor.fetchone()
        if resultado and resultado.get('plano'):
            return resultado['plano']
    except Exception as e:
        print(f"Erro ao buscar plano do usuário: {e}")
    return 'freemium'

# ===================================
# Rotas de Autenticação e Usuário
# ===================================
@app.route('/')
def index():
    return 'API ON', 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios.'}), 400

    cursor.execute('SELECT id_aluno, nome, email, plano, url_foto FROM Aluno WHERE email = %s AND senha = %s', (email, senha))
    usuario = cursor.fetchone()

    if usuario:
        session['id_aluno'] = usuario['id_aluno']
        session['plano'] = usuario['plano']
        return jsonify({'message': 'Login realizado com sucesso!', 'user': usuario}), 200
    else:
        return jsonify({'error': 'Email ou senha inválidos.'}), 401

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    try:
        cursor.execute('INSERT INTO Aluno (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, senha))
        conn.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso.'}), 201
    except IntegrityError:
        return jsonify({'error': 'Email já cadastrado.'}), 400

@app.route('/editar_usuario/<int:id_aluno>', methods=['PUT'])
def editar_usuario(id_aluno):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    url_foto = data.get('url_foto')

    campos = []
    valores = []

    if nome:
        campos.append("nome=%s")
        valores.append(nome)
    if email:
        campos.append("email=%s")
        valores.append(email)
    if senha:
        campos.append("senha=%s")
        valores.append(senha)
    if url_foto is not None:
        campos.append("url_foto=%s")
        valores.append(url_foto)

    if not campos:
        return jsonify({'error': 'Nenhum campo para atualizar.'}), 400

    query = f"UPDATE Aluno SET {', '.join(campos)} WHERE id_aluno=%s"
    valores.append(id_aluno)

    cursor.execute(query, tuple(valores))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário atualizado com sucesso.'})


@app.route('/excluir_usuario/<int:id_aluno>', methods=['DELETE'])
def excluir_usuario(id_aluno):
    cursor.execute('DELETE FROM Aluno WHERE id_aluno=%s', (id_aluno,))
    conn.commit()
    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404
    return jsonify({'message': 'Usuário excluído com sucesso.'})

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    cursor.execute('SELECT id_aluno, nome, email, url_foto, plano FROM Aluno')
    usuarios = cursor.fetchall()
    return jsonify(usuarios)


# ===================================
# Rotas de Conteúdo (Com Lógica de Planos)
# ===================================

@app.route('/quiz', methods=['POST'])
def quiz():
    data = request.get_json()
    id_aluno = data.get('id_aluno') 
    
    if not id_aluno:
        return jsonify({'error': 'ID do aluno é obrigatório.'}), 400

    plano_usuario = get_user_plan(id_aluno)
    
    # --- LÓGICA PARA PLANO FREEMIUM ---
    if plano_usuario == 'freemium':
        categoria = data.get('category', 'ambos')
        todas_as_perguntas = carregar_dados_json('questions.json')
        
        if not todas_as_perguntas:
             return jsonify({'error': 'Não foi possível carregar as perguntas.'}), 500

        perguntas_filtradas = []
        if categoria == 'ambos':
            perguntas_filosofia = [p for p in todas_as_perguntas if p.get('category') == 'filosofia']
            perguntas_sociologia = [p for p in todas_as_perguntas if p.get('category') == 'sociologia']
            random.shuffle(perguntas_filosofia)
            random.shuffle(perguntas_sociologia)
            perguntas_filtradas.extend(perguntas_filosofia[:5])
            perguntas_filtradas.extend(perguntas_sociologia[:5])
        else:
            perguntas_filtradas = [p for p in todas_as_perguntas if p.get('category') == categoria]

        random.shuffle(perguntas_filtradas)
        return jsonify(perguntas_filtradas[:10])

    # --- LÓGICA PARA PLANO PREMIUM ---
    # CORREÇÃO: Revertido para a lógica original que o front-end espera
    elif plano_usuario == 'premium':
        if 'tema' not in data:
            return jsonify({'error': 'O campo "tema" é obrigatório para usuários Premium.'}), 400
        
        tema = data['tema']
        prompt = f"""Dado o tema '{tema}', primeiro avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo preconceituoso, sexual, violento ou inadequado de qualquer tipo.

Se o tema for válido, gere um quiz com 10 questões sobre ele. Retorne as questões **APENAS** em formato JSON, sem qualquer texto adicional, formatação Markdown de blocos de código ou outros caracteres fora do JSON. Cada questão deve ser um objeto com as seguintes chaves:
- "pergunta": (string) O texto da pergunta.
- "opcoes": (array de strings) Um array com 4 opções de resposta.
- "resposta_correta": (string) O texto exato de uma das opções.
- "explicacao": (string) Uma breve explicação (1-2 frases) do porquê a resposta correta está certa.
**as quetões devem ser variadas de um quiz para outro, evite repetir as mesmas perguntas.

Se o tema for inválido, retorne **APENAS** a mensagem: NÃO É POSSIVEL FORMAR UMA RESPOSTA DEVIDO A INADEQUAÇÃO DO ASSUNTO.
"""
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            texto = response.text.strip()
            # Retorna o texto bruto para o front-end processar
            return jsonify({"assunto": tema, "contedo": texto})
        except Exception as e:
            return jsonify({"erro": f"Erro ao gerar quiz com IA: {str(e)}"}), 500
    
    return jsonify({"error": "Plano de usuário inválido."}), 403


@app.route('/flashcard', methods=['POST'])
def flashcard():
    data = request.get_json()
    id_aluno = data.get('id_aluno')

    if not id_aluno:
        return jsonify({'error': 'ID do aluno é obrigatório.'}), 400

    plano_usuario = get_user_plan(id_aluno)

    # --- LÓGICA PARA PLANO FREEMIUM ---
    if plano_usuario == 'freemium':
        categoria = data.get('category', 'ambos')
        todos_flashcards = carregar_dados_json('flashcards.json')
        
        if not todos_flashcards:
            return jsonify({'error': 'Não foi possível carregar os flashcards.'}), 500
        
        flashcards_filtrados = []
        if categoria == 'ambos':
            flashcards_filosofia = [f for f in todos_flashcards if f.get('category') == 'filosofia']
            flashcards_sociologia = [f for f in todos_flashcards if f.get('category') == 'sociologia']
            random.shuffle(flashcards_filosofia)
            random.shuffle(flashcards_sociologia)
            flashcards_filtrados.extend(flashcards_filosofia[:4])
            flashcards_filtrados.extend(flashcards_sociologia[:4])
        else:
            flashcards_filtrados = [f for f in todos_flashcards if f.get('category') == categoria]
        
        random.shuffle(flashcards_filtrados)
        return jsonify(flashcards_filtrados[:8])

    # --- LÓGICA PARA PLANO PREMIUM (Original) ---
    # CORREÇÃO: Revertido para a lógica original que o front-end espera
    elif plano_usuario == 'premium':
        if 'tema' not in data:
            return jsonify({'error': 'O campo "tema" é obrigatório para usuários Premium.'}), 400
        
        tema = data['tema']
        prompt = f"""
Dado o tema '{tema}', primeiro avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo inadequado.

Se o tema for válido, Gere 12 perguntas para flashcards sobre o tema '{tema}'. Retorne a pergunta e a resposta correta, a resposta deve ser breve e acertiva. Estrutura: Pergunta: [pergunta] Resposta: [resposta]

Se o tema for inválido, retorne **APENAS** a mensagem: NÃO É POSSIVEL FORMAR UMA RESPOSTA DEVIDO A INADEQUAÇÃO DO ASSUNTO.
"""
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            texto = response.text.strip()
            # Retorna o texto bruto para o front-end processar
            return jsonify({"assunto": tema, "contedo": texto})
        except Exception as e:
            return jsonify({"erro": f"Erro ao gerar flashcards com IA: {str(e)}"}), 500
            
    return jsonify({"error": "Plano de usuário inválido."}), 403

# --- Rotas Originais de Geração de Conteúdo (Acesso Premium) ---
@app.route('/resumo', methods=['POST'])
def resumo():
    data = request.get_json()
    id_aluno = data.get('id_aluno')
    
    if not id_aluno or get_user_plan(id_aluno) != 'premium':
        return jsonify({'error': 'Esta funcionalidade é exclusiva para usuários Premium.'}), 403

    if 'tema' not in data:
        return jsonify({'error': 'O campo "tema" é obrigatório.'}), 400
    
    tema = data['tema']
    prompt = f"""
        Dado o tema '{tema}', avalie se ele é estritamente relacionado a filosofia ou sociologia e não contém conteúdo inadequado.
        O resumo deve ser focado nos principais tópicos do tema.
        Se o tema for inválido, retorne **APENAS** a mensagem: NÃO É POSSIVEL FORMAR UMA RESPOSTA DEVIDO A INADEQUAÇÃO DO ASSUNTO.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "conteudo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/correcao', methods=['POST'])
def correcao():
    data = request.get_json()
    id_aluno = data.get('id_aluno')

    if not id_aluno or get_user_plan(id_aluno) != 'premium':
        return jsonify({'error': 'Esta funcionalidade é exclusiva para usuários Premium.'}), 403

    if 'tema' not in data or 'texto' not in data:
        return jsonify({'error': 'Os campos "tema" e "texto" são obrigatórios.'}), 400

    tema = data['tema']
    texto = data['texto']
    prompt = f""""
        Você é um professor especializado em Filosofia e Sociologia. Corrija o texto do aluno sobre o tema '{tema}'.
        Texto do aluno: '{texto}'.
        Seu feedback deve ser resumido e focado no conteúdo, não na gramática.
        Avalie se o tema é apropriado. Se não for, retorne **APENAS** a mensagem: NÃO É POSSIVEL FORMAR UMA RESPOSTA DEVIDO A INADEQUAÇÃO DO ASSUNTO.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        texto_corrigido = response.text.strip()
        return jsonify({"texto_original": texto, "correcao": texto_corrigido})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ===================================
# Chatbot com SocketIO (Acesso para todos os planos)
# ===================================
instrucoes = """Você é um assistente de IA focado em ajudar estudantes com temas de filosofia e sociologia, de maneira didática e interativa."""
active_chats = {}

def get_user_chat():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())

    session_id = session['session_id']
    if session_id not in active_chats:
        model = genai.GenerativeModel(MODEL_NAME)
        chat_session = model.start_chat(history=[
            {"role": "user", "parts": [{"text": instrucoes}]},
            {"role": "model", "parts": [{"text": "Olá! Sou seu assistente de estudos em Filosofia e Sociologia. Como posso ajudar você hoje?"}]}
        ])
        active_chats[session_id] = chat_session
    return active_chats[session_id]

@socketio.on('connect')
def handle_connect():
    emit('status_conexao', {'data': 'Conectado com sucesso!'})
    user_chat = get_user_chat()
    welcome_message = user_chat.history[-1].parts[0].text
    emit('nova_mensagem', {"remetente": "bot", "texto": welcome_message})

@socketio.on('enviar_mensagem')
def handle_enviar_mensagem(data):
    mensagem_usuario = data.get("mensagem")
    if not mensagem_usuario:
        emit('erro', {"erro": "Mensagem não pode ser vazia."})
        return
    
    try:
        user_chat = get_user_chat()
        resposta = user_chat.send_message(mensagem_usuario)
        emit('nova_mensagem', {"remetente": "bot", "texto": resposta.text})
    except Exception as e:
        emit('erro', {'erro': f'Ocorreu um erro na IA: {str(e)}'})

# --- Inicialização ---
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)no, nome, email, plano FROM Aluno WHERE email = %s AND senha = %s', (email, senha))
    usuario = cursor.fetchone()

    if usuario:
        session['id_aluno'] = usuario['id_aluno']
        session['plano'] = usuario['plano']
        return jsonify({'message': 'Login realizado com sucesso!', 'user': usuario}), 200
    else:
        return jsonify({'error': 'Email ou senha inválidos.'}), 401

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    try:
        # Novos usuários começam como 'freemium' por padrão
        cursor.execute('INSERT INTO Aluno (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, senha))
        conn.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso.'}), 201
    except IntegrityError:
        return jsonify({'error': 'Email já cadastrado.'}), 400

@app.route('/editar_usuario/<int:id_aluno>', methods=['PUT'])
def editar_usuario(id_aluno):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    url_foto = data.get('url_foto')

    campos = []
    valores = []

    if nome:
        campos.append("nome=%s")
        valores.append(nome)
    if email:
        campos.append("email=%s")
        valores.append(email)
    if senha: # Em um app real, a senha deve ser hasheada
        campos.append("senha=%s")
        valores.append(senha)
    if url_foto:
        campos.append("url_foto=%s")
        valores.append(url_foto)

    if not campos:
        return jsonify({'error': 'Nenhum campo para atualizar.'}), 400

    query = f"UPDATE Aluno SET {', '.join(campos)} WHERE id_aluno=%s"
    valores.append(id_aluno)

    cursor.execute(query, tuple(valores))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário atualizado com sucesso.'})


@app.route('/excluir_usuario/<int:id_aluno>', methods=['DELETE'])
def excluir_usuario(id_aluno):
    cursor.execute('DELETE FROM Aluno WHERE id_aluno=%s', (id_aluno,))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Usuário não encontrado.'}), 404

    return jsonify({'message': 'Usuário excluído com sucesso.'})

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    cursor.execute('SELECT id_aluno, nome, email, url_foto, plano FROM Aluno')
    usuarios = cursor.fetchall()
    return jsonify(usuarios)


# ===================================
# Rotas de Conteúdo (Com Lógica de Planos)
# ===================================

@app.route('/quiz', methods=['POST'])
def quiz():
    # Para o Quiz, vamos assumir que o ID do aluno é enviado no corpo da requisição
    # Em um sistema real, você pegaria isso da sessão de login
    data = request.get_json()
    id_aluno = data.get('id_aluno') 
    
    if not id_aluno:
        return jsonify({'error': 'ID do aluno é obrigatório.'}), 400

    plano_usuario = get_user_plan(id_aluno)
    
    # --- LÓGICA PARA PLANO FREEMIUM ---
    if plano_usuario == 'freemium':
        categoria = data.get('category', 'ambos')
        todas_as_perguntas = carregar_dados_json('questions.json')
        
        if not todas_as_perguntas:
             return jsonify({'error': 'Não foi possível carregar as perguntas.'}), 500

        if categoria == 'ambos':
            perguntas_filosofia = [p for p in todas_as_perguntas if p.get('category') == 'filosofia']
            perguntas_sociologia = [p for p in todas_as_perguntas if p.get('category') == 'sociologia']
            random.shuffle(perguntas_filosofia)
            random.shuffle(perguntas_sociologia)
            perguntas_filtradas = perguntas_filosofia[:5] + perguntas_sociologia[:5]
        else:
            perguntas_filtradas = [p for p in todas_as_perguntas if p.get('category') == categoria]

        random.shuffle(perguntas_filtradas)
        return jsonify(perguntas_filtradas[:10])

    # --- LÓGICA PARA PLANO PREMIUM (Original) ---
    elif plano_usuario == 'premium':
        if 'tema' not in data:
            return jsonify({'error': 'O campo "tema" é obrigatório para usuários Premium.'}), 400
        
        tema = data['tema']
        prompt = f"""
            Dado o tema '{tema}', que deve ser estritamente relacionado a filosofia ou sociologia e não conter conteúdo inadequado, gere um quiz com 10 questões.
            Retorne as questões **APENAS** em formato JSON, sem texto adicional.
            Cada questão deve ser um objeto com as chaves: "question", "options" (array de 4 strings), "correctAnswer" (string da resposta correta) e "explicacao" (breve justificativa).
            **Varie as perguntas para cada requisição.**

            Se o tema for inválido, retorne um JSON com a chave "error_message".
        """
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            # Tenta limpar e carregar o JSON da resposta da IA
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            quiz_data = json.loads(cleaned_response)
            return jsonify(quiz_data)
        except Exception as e:
            return jsonify({"erro": f"Erro ao gerar quiz com IA: {str(e)}"}), 500
    
    return jsonify({"error": "Plano de usuário inválido."}), 403


@app.route('/flashcard', methods=['POST'])
def flashcard():
    data = request.get_json()
    id_aluno = data.get('id_aluno')

    if not id_aluno:
        return jsonify({'error': 'ID do aluno é obrigatório.'}), 400

    plano_usuario = get_user_plan(id_aluno)

    # --- LÓGICA PARA PLANO FREEMIUM ---
    if plano_usuario == 'freemium':
        categoria = data.get('category', 'ambos')
        todos_flashcards = carregar_dados_json('flashcards.json')
        
        if not todos_flashcards:
            return jsonify({'error': 'Não foi possível carregar os flashcards.'}), 500

        if categoria == 'ambos':
            flashcards_filosofia = [f for f in todos_flashcards if f.get('category') == 'filosofia']
            flashcards_sociologia = [f for f in todos_flashcards if f.get('category') == 'sociologia']
            random.shuffle(flashcards_filosofia)
            random.shuffle(flashcards_sociologia)
            flashcards_filtrados = flashcards_filosofia[:4] + flashcards_sociologia[:4]
        else:
            flashcards_filtrados = [f for f in todos_flashcards if f.get('category') == categoria]
        
        random.shuffle(flashcards_filtrados)
        return jsonify(flashcards_filtrados[:8])

    # --- LÓGICA PARA PLANO PREMIUM (Original) ---
    elif plano_usuario == 'premium':
        if 'tema' not in data:
            return jsonify({'error': 'O campo "tema" é obrigatório para usuários Premium.'}), 400
        
        tema = data['tema']
        prompt = f"""
            Dado o tema '{tema}', que deve ser estritamente de filosofia ou sociologia e sem conteúdo inadequado, gere 8 flashcards.
            Para cada um, retorne a pergunta e a resposta. A resposta deve ser breve e assertiva.
            Formato de saída: **APENAS** uma lista de objetos JSON, cada um com as chaves "pergunta", "resposta", "explicacao" e "category".

            Se o tema for inválido, retorne um JSON com "error_message".
        """
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            flashcard_data = json.loads(cleaned_response)
            return jsonify(flashcard_data)
        except Exception as e:
            return jsonify({"erro": f"Erro ao gerar flashcards com IA: {str(e)}"}), 500
            
    return jsonify({"error": "Plano de usuário inválido."}), 403

# --- Rotas Originais de Geração de Conteúdo (Acesso Premium) ---
# Estas rotas agora podem ser consideradas exclusivas para planos Premium
@app.route('/resumo', methods=['POST'])
def resumo():
    data = request.get_json()
    id_aluno = data.get('id_aluno')
    
    if get_user_plan(id_aluno) != 'premium':
        return jsonify({'error': 'Esta funcionalidade é exclusiva para usuários Premium.'}), 403

    if 'tema' not in data:
        return jsonify({'error': 'O campo "tema" é obrigatório.'}), 400
    
    tema = data['tema']
    prompt = f"""
        Dado o tema '{tema}', avalie se ele é estritamente relacionado a filosofia ou sociologia e se não contém conteúdo inadequado.
        O resumo deve ser focado nos principais tópicos do tema.
        Se o tema for inválido, retorne **APENAS** um JSON com "error_message".
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return jsonify({"assunto": tema, "conteudo": texto})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/correcao', methods=['POST'])
def correcao():
    data = request.get_json()
    id_aluno = data.get('id_aluno')

    if get_user_plan(id_aluno) != 'premium':
        return jsonify({'error': 'Esta funcionalidade é exclusiva para usuários Premium.'}), 403

    if 'tema' not in data or 'texto' not in data:
        return jsonify({'error': 'Os campos "tema" e "texto" são obrigatórios.'}), 400

    tema = data['tema']
    texto = data['texto']
    prompt = f""""
        Você é um professor especializado em Filosofia e Sociologia. Corrija o texto do aluno sobre o tema '{tema}'.
        Texto do aluno: '{texto}'.
        Seu feedback deve ser resumido e focado no conteúdo, não na gramática.
        Avalie se o tema é apropriado. Se não for, retorne um JSON com "error_message".
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        texto_corrigido = response.text.strip()
        return jsonify({"texto_original": texto, "correcao": texto_corrigido})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ===================================
# Chatbot com SocketIO (Acesso para todos os planos)
# ===================================
instrucoes = """Você é um assistente de IA focado em ajudar estudantes com temas de filosofia e sociologia, de maneira didática e interativa."""
active_chats = {}

def get_user_chat():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())

    session_id = session['session_id']
    if session_id not in active_chats:
        model = genai.GenerativeModel(MODEL_NAME)
        chat_session = model.start_chat(history=[
            {"role": "user", "parts": [{"text": instrucoes}]},
            {"role": "model", "parts": [{"text": "Olá! Sou seu assistente de estudos em Filosofia e Sociologia. Como posso ajudar você hoje?"}]}
        ])
        active_chats[session_id] = chat_session
    return active_chats[session_id]

@socketio.on('connect')
def handle_connect():
    emit('status_conexao', {'data': 'Conectado com sucesso!'})
    user_chat = get_user_chat()
    welcome_message = user_chat.history[-1].parts[0].text
    emit('nova_mensagem', {"remetente": "bot", "texto": welcome_message})

@socketio.on('enviar_mensagem')
def handle_enviar_mensagem(data):
    mensagem_usuario = data.get("mensagem")
    if not mensagem_usuario:
        emit('erro', {"erro": "Mensagem não pode ser vazia."})
        return
    
    try:
        user_chat = get_user_chat()
        resposta = user_chat.send_message(mensagem_usuario)
        emit('nova_mensagem', {"remetente": "bot", "texto": resposta.text})
    except Exception as e:
        emit('erro', {'erro': f'Ocorreu um erro na IA: {str(e)}'})

# --- Inicialização ---
if __name__ == "__main__":
    # Use uma porta diferente se o front-end estiver rodando na 5000
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)