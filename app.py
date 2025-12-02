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
    return render_template('leaderboards.html')

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

@app.route('/0h_h1')
def page_0hh1():
    n = request.args.get('n')
    return render_template('0h_h1.html', n=n)

@app.route('/0h_h1_tt')
def page_0hh1_tt():
    return render_template('0h_h1_tt.html')


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
    

if __name__ == '__main__':
    app.run(debug=True)