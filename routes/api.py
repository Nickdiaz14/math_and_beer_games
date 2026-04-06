from flask import Blueprint, request, jsonify
from datetime import datetime
import pytz
import random
from db import get_connection, release_connection

api_bp = Blueprint('api', __name__)

@api_bp.route('/attendance', methods=['POST'])
def attendance():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        data = request.form
        timezone = pytz.timezone('America/Bogota')
        now = datetime.now(timezone)
        fecha_corta = now.strftime('%Y/%m/%d')
        fecha_larga = now.strftime('%Y/%m/%d %H:%M')
        
        cursor.execute("""
            INSERT INTO attendance 
            (created_at, "Fecha", "Nombre", "Sexo", "Edad", "Correo", "Rol", "Calificación", "Futuros_eventos", "Comentario", "Tipo_documento", "Numero_documento", "Konradista", "Ciudad", "Carrera")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (fecha_larga, fecha_corta, data['nombre_completo'], data['sexo'], data['edad'], 
              data['correo_electronico'], data['rol'], data['calificacion'], data['futuros_eventos'], 
              data['comentario'], data['tipo_doc'], data['numero_doc'], data['konradista'], data['ciudad'], data['carrera']))
        connection.commit()
    except Exception as e:
        print("Error attendance:", e)
        return jsonify({'success': False})
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'success': True})

@api_bp.route('/0h_h1/play', methods=['POST'])
def get_cond_ini():
    n = request.json['n'] 
    with open(f'static/boards/aleatorios{n}.txt', 'r', encoding='utf-8') as file:
        lineas = file.readlines()
        linea_especifica = lineas[random.randint(0, len(lineas)-1)].strip()
    return jsonify({'matrix': eval(linea_especifica)})

@api_bp.route('/leaderboard/submit', methods=['POST'])
def update_leaderboard():
    better = False
    user_id = request.json['userid']
    board = request.json['game']
    record_raw = request.json['record']
    
    count_games = ['TContrareloj', 'TUnicolor', 'TBicolor', 'TProgresivo', 'TAleatorio']
    points_games = ['TCruzado', 'TKnight', 'TMini-Nerdle', 'TNerdle', 'TMaxi-Nerdle']

    connection = get_connection()
    try:
        cursor = connection.cursor()
        
        if board in count_games:
            record = int(record_raw)
            string_record = f'{record} tabs'
            is_better = lambda new, old: new > old
        elif board in points_games:
            record = float(record_raw)
            string_record = f'{round(record, 2)}'
            is_better = lambda new, old: new > old
        else:
            record = int(record_raw)
            string_record = f'{(record//6000):02}:{((record%6000)//100):02}.{(record%100):02}'
            is_better = lambda new, old: new < old

        cursor.execute("SELECT id, record FROM leaderboard WHERE userid = %s AND board = %s;", (user_id, board))
        prev_record = cursor.fetchone()

        if prev_record:
            lead_id = int(prev_record[0])
            prev_value = float(prev_record[1]) if board in points_games else int(prev_record[1])

            if is_better(record, prev_value):
                cursor.execute("UPDATE leaderboard SET record = %s, string_record = %s WHERE id = %s;", (record, string_record, lead_id))
                better = True
        else:
            cursor.execute("INSERT INTO leaderboard (board, userid, record, string_record) VALUES (%s, %s, %s, %s);", (board, user_id, record, string_record))

        connection.commit()
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'better': better})

@api_bp.route('/leaderboard/consult', methods=['POST'])
def get_leaderboard():
    user_id = request.json['userid']
    board = request.json['game']
    desc = ['TContrareloj', 'TUnicolor', 'TBicolor', 'TProgresivo', 'TAleatorio', 'TCruzado', 'TKnight', 'TMini-Nerdle', 'TNerdle', 'TMaxi-Nerdle']
    order_type = "DESC" if board in desc else ""

    connection = get_connection()
    try:
        cursor = connection.cursor()
        
        query = f"""
            SELECT ROW_NUMBER() OVER (PARTITION BY board ORDER BY record {order_type}) AS position,
                   nickname, string_record, userid
            FROM leader_final_view WHERE board = %s;
        """
        cursor.execute(query, (board,))
        ranking = cursor.fetchall()

        query_2 = f"""
            SELECT * FROM (
                SELECT ROW_NUMBER() OVER (PARTITION BY board ORDER BY record {order_type}) AS position,
                       nickname, string_record, userid
                FROM leader_final_view WHERE board = %s
            ) t WHERE t.userid = %s
        """
        cursor.execute(query_2, (board, user_id))
        personal_ranking = cursor.fetchone()
    finally:
        cursor.close()
        release_connection(connection)

    if personal_ranking and personal_ranking[0] > 0:
        return jsonify({'ranking': ranking, 'personal_ranking': personal_ranking, 'count_records': len(ranking)})
        
    return jsonify({'ranking': ranking, 'personal_ranking': ['-', '-', '-', '-'], 'count_records': len(ranking)})

@api_bp.route('/seeUser', methods=['POST'])
def seeUserExistense():
    user_id = request.json['user_id'] 
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT nickname FROM nickname WHERE userid = %s;", (user_id,))
        name = cursor.fetchone()
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'valid': True if name else False})

@api_bp.route('/generateUser', methods=['POST'])
def generateUser():
    user_id = request.json['user_id']
    nickname = request.json['nickname'].strip()

    if len(nickname) > 20:
        return jsonify({'valid': False, 'message_id': 1})

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM nickname WHERE LOWER(nickname) = LOWER(%s) AND userid != %s;", (nickname, user_id))
        if cursor.fetchone():
            return jsonify({'valid': False, 'message_id': 0})
        cursor.execute("INSERT INTO nickname (userid, nickname) VALUES (%s, %s);", (user_id, nickname))
        connection.commit()
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'valid': True, 'message_id': ''})

# --- BLOG ROUTES ---
@api_bp.route('/api/comments/<int:event_id>', methods=['GET'])
def get_comments(event_id):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT c.id, n.nickname, c.content, c.created_at
            FROM comments c JOIN nickname n ON n.userid = c.userid
            WHERE c.event_id = %s ORDER BY c.created_at ASC;
        """, (event_id,))
        rows = cursor.fetchall()
        comments = [{'id': r[0], 'nickname': r[1], 'content': r[2], 'created_at': r[3].isoformat()} for r in rows]
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'comments': comments})

@api_bp.route('/api/comments/add', methods=['POST'])
def add_comment():
    user_id = request.json.get('userid')
    event_id = request.json.get('event_id')
    content = request.json.get('content', '').strip()

    if not user_id or not event_id or not content:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    if len(content) > 500:
        return jsonify({'success': False, 'message': 'Comentario muy largo'}), 400

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT nickname FROM nickname WHERE userid = %s;", (user_id,))
        nick_row = cursor.fetchone()
        if not nick_row:
            return jsonify({'success': False, 'message': 'Debes crear un Nickname para comentar'}), 403

        cursor.execute("INSERT INTO comments (event_id, userid, content) VALUES (%s, %s, %s) RETURNING id, created_at;", (event_id, user_id, content))
        row = cursor.fetchone()
        connection.commit()
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'success': True, 'id': row[0], 'nickname': nick_row[0], 'created_at': row[1].isoformat()})

@api_bp.route('/api/reactions/<int:event_id>', methods=['GET'])
def get_reactions(event_id):
    user_id = request.args.get('userid', '')
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM reactions WHERE event_id = %s;", (event_id,))
        total = cursor.fetchone()[0]
        reacted = False
        if user_id:
            cursor.execute("SELECT 1 FROM reactions WHERE event_id = %s AND userid = %s;", (event_id, user_id))
            reacted = cursor.fetchone() is not None
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'total': total, 'reacted': reacted})

@api_bp.route('/api/reactions/toggle', methods=['POST'])
def toggle_reaction():
    user_id = request.json.get('userid')
    event_id = request.json.get('event_id')
    if not user_id or not event_id: return jsonify({'success': False}), 400

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM reactions WHERE event_id = %s AND userid = %s;", (event_id, user_id))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("DELETE FROM reactions WHERE id = %s;", (existing[0],))
            reacted = False
        else:
            cursor.execute("INSERT INTO reactions (event_id, userid) VALUES (%s, %s);", (event_id, user_id))
            reacted = True
        cursor.execute("SELECT COUNT(*) FROM reactions WHERE event_id = %s;", (event_id,))
        total = cursor.fetchone()[0]
        connection.commit()
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'success': True, 'reacted': reacted, 'total': total})

@api_bp.route('/api/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email', '').strip().lower()
    name = request.json.get('name', '').strip()
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Correo inválido'}), 400
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO subscribers (email, name) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING;", (email, name or None))
        connection.commit()
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        release_connection(connection)
    return jsonify({'success': True})
