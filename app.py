from flask import Flask, render_template, request, jsonify
import pytz
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def menu():
    return render_template('about.html')

@app.route('/leaderboards')
def leaderboards():
    return render_template('leaderboards.html')

@app.route('/menu')
def about():
    return render_template('menu.html')

@app.route('/forms')
def forms():
    return render_template('forms.html')


# Conectar a Supabase
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
        comentario = request.form['comentario']
        timezone = pytz.timezone('America/Bogota')
        now = datetime.now(timezone)
        fecha_corta = now.strftime('%Y/%m/%d')
        fecha_larga = now.strftime('%Y/%m/%d %H:%M')
        cursor.execute("""
                INSERT INTO attendance 
                (created_at, "Fecha", "Nombre", "Sexo", "Edad", "Correo", "Rol", "Calificación", "Futuros_eventos", "Comentario", "Tipo_documento", "Numero_documento")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (fecha_larga, fecha_corta, nombre_completo, sexo, edad, correo_electronico, rol, calificacion, futuros_eventos, comentario,tipo_doc, numero_doc))

        connection.commit()
        cursor.close()
        connection.close()  
        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)