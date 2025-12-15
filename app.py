from flask import Flask, render_template, request, jsonify
from datetime import datetime
import psycopg2
import random
import pytz
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Templates
@app.route('/')
def page_about():
    with open("static/json/equipo.json", "r", encoding="utf-8") as f:
        equipo = json.load(f)

    with open("static/json/charlas.json", "r", encoding="utf-8") as f:
        charlas = json.load(f)

    grouped = {}
    for c in charlas:
        grouped.setdefault(c["year"], []).append(c)

    return render_template("about.html", charlas=grouped, miembros=equipo)

@app.route('/leaderboards')
def page_leaderboards():
    return render_template('leaderboards.html', records=10)

@app.route('/menu_games')
def page_menu():
    id = request.args.get('userid')
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT nickname FROM nickname
        WHERE userid = %s;
    """, (id,))

    name = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()  
    return render_template('menu.html', nickname=name)

@app.route('/forms')
def page_forms():
    return render_template('forms.html')

@app.route('/register')
def page_register():
    try:
        m = request.args.get('m')
        return render_template('register.html', m = m)
    except:
        return render_template('registrer.html')

@app.route('/0h_h1')
def page_0hh1():
    n = request.args.get('n')
    return render_template('0h_h1.html', n=n)

@app.route('/0h_h1_tt')
def page_0hh1_tt():
    return render_template('0h_h1_tt.html')

@app.route('/knight')
def page_knight():
    return render_template('knight.html')

@app.route('/secuenzo')
def page_secuenzo():
    n = request.args.get('n')
    return render_template('secuenzo.html', n=n)

@app.route('/leaderboard')
def page_leaderboard():
    game = request.args.get('game')
    name = request.args.get('name')
    return render_template('leaderboard.html', game = game, name = name, records = 5)

# Conección a Base de Datos
def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port="5432"
    )

#---------------------------------------------------------attendance---------------------------------------------------------#
@app.route('/attendance', methods=['POST'])
def attendance():
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Procesar los datos
        nombre_completo = request.form['nombre_completo']
        sexo = request.form['sexo']
        edad = request.form['edad']
        correo_electronico = request.form['correo_electronico']
        rol = request.form['rol']
        calificacion = request.form['calificacion']
        futuros_eventos = request.form['futuros_eventos']
        tipo_doc = request.form['tipo_doc']
        numero_doc = request.form['numero_doc']
        konradista = request.form['konradista']
        comentario = request.form['comentario']
        timezone = pytz.timezone('America/Bogota')
        now = datetime.now(timezone)
        fecha_corta = now.strftime('%Y/%m/%d')
        fecha_larga = now.strftime('%Y/%m/%d %H:%M')
        cursor.execute("""
                INSERT INTO attendance 
                (created_at, "Fecha", "Nombre", "Sexo", "Edad", "Correo", "Rol", "Calificación", "Futuros_eventos", "Comentario", "Tipo_documento", "Numero_documento", "Konradista")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (fecha_larga, fecha_corta, nombre_completo, sexo, edad, correo_electronico, rol, calificacion, futuros_eventos, comentario,tipo_doc, numero_doc, konradista))

        connection.commit()
        cursor.close()
        connection.close()  
        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False})
    
#---------------------------------------------------------Fetch---------------------------------------------------------#

@app.route('/0h_h1/play', methods=['POST'])
def get_cond_ini():
    n = request.json['n'] 
    with open(f'static/boards/aleatorios{n}.txt', 'r', encoding='utf-8') as file:
        lineas = file.readlines()
        linea_especifica = lineas[random.randint(0, len(lineas)-1)].strip()  # Remueve espacios en blanco y saltos de línea
    matrix = eval(linea_especifica)

    return jsonify({'matrix': matrix})

@app.route('/leaderboard/submit', methods=['POST'])
def update_leaderboard():
    better = False
    user_id = request.json['userid']
    board = request.json['game']
    record_raw = request.json['record']
    
    count_games = ['TContrareloj', 'TUnicolor', 'TBicolor', 'TProgresivo', 'TAleatorio']
    points_games = ['TCruzado', 'TKnight', 'TMini-Nerdle', 'TNerdle', 'TMaxi-Nerdle']

    connection = connect_db()
    cursor = connection.cursor()
    
    try:
        # Convertir y formatear record según el tipo de juego
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

        cursor.execute("""
            SELECT id, record FROM leaderboard
            WHERE userid = %s AND board = %s;
        """, (user_id, board))

        prev_record = cursor.fetchone()

        if prev_record:
            lead_id = int(prev_record[0])
            prev_value = float(prev_record[1]) if board in points_games else int(prev_record[1])

            print(prev_value, record)
            
            if is_better(record, prev_value):
                cursor.execute("""
                    UPDATE leaderboard
                    SET record = %s, string_record = %s
                    WHERE id = %s;
                """, (record, string_record, lead_id))
                better = True
        else:
            cursor.execute("""
                INSERT INTO leaderboard (board, userid, record, string_record)
                VALUES (%s, %s, %s, %s);
            """, (board, user_id, record, string_record))

        connection.commit()

    except Exception as e:
        connection.rollback()
        print("Error:", e)
        return jsonify({'error': str(e)}), 500
        
    finally:
        cursor.close()
        connection.close() 

    return jsonify({'better': better})

@app.route('/leaderboard/consult', methods=['POST'])
def get_leaderboard():
    user_id = request.json['userid']
    board = request.json['game']
    records = request.json['records']
    connection = connect_db()
    cursor = connection.cursor()

    desc = ['TContrareloj', 'TUnicolor', 'TBicolor', 'TProgresivo', 'TAleatorio', 'TCruzado', 'TKnight', 'TMini-Nerdle', 'TNerdle', 'TMaxi-Nerdle']
    
    query = """
        SELECT
            ROW_NUMBER() OVER (PARTITION BY board ORDER BY record DESC) AS position,
            nickname,
            string_record,
            userid
        FROM leader_final_view
        WHERE board = %s
        LIMIT %s;
    """ if board in desc else """
        SELECT
            ROW_NUMBER() OVER (PARTITION BY board ORDER BY record) AS position,
            nickname,
            string_record,
            userid
        FROM leader_final_view
        WHERE board = %s
        LIMIT %s;
    """
    cursor.execute(query, (board, records))

    ranking = cursor.fetchall()

    query_2 = """
        SELECT * FROM (SELECT
            ROW_NUMBER() OVER (PARTITION BY board ORDER BY record DESC) AS position,
            nickname,
            string_record,
            userid
        FROM leader_final_view
        WHERE board = %s) t
        WHERE t.userid = %s
    """ if board in desc else """
        SELECT * FROM (SELECT
            ROW_NUMBER() OVER (PARTITION BY board ORDER BY record) AS position,
            nickname,
            string_record,
            userid
        FROM leader_final_view
        WHERE board = %s) t
        WHERE t.userid = %s
    """
    cursor.execute(query_2, (board,user_id))
    personal_ranking = cursor.fetchone()
    if personal_ranking:
        if personal_ranking[0] > 0:
            return jsonify({'ranking': ranking, 'personal_ranking': personal_ranking})
        
    return jsonify({'ranking': ranking, 'personal_ranking': ['-', '-', '-', '-']})

@app.route('/seeUser', methods=['POST'])
def seeUserExistense():
    user_id = request.json['user_id'] 
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT nickname FROM nickname
        WHERE userid = %s;
    """, (user_id,))

    name = cursor.fetchone()
    cursor.close()
    connection.close()  
    return jsonify({'valid': True if name else False})

@app.route('/generateUser', methods=['POST'])
def generateUser():
    user_id = request.json['user_id']
    nickname = request.json['nickname'].strip()

    if len(nickname) > 20:
        return jsonify({'valid': False, 'message_id': 1})

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 1 FROM nickname
        WHERE LOWER(nickname) = LOWER(%s)
        AND userid != %s;
    """, (nickname, user_id))

    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({'valid': False, 'message_id': 0})

    cursor.execute("""
        INSERT INTO nickname (userid, nickname)
        VALUES (%s, %s);
    """, (user_id, nickname))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'valid': True, 'message_id': -1})

    

if __name__ == '__main__':
    app.run(debug=True)