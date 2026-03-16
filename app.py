from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def conectar():
    return sqlite3.connect("database.db")


def crear_tabla():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tareas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        fecha TEXT,
        completada INTEGER
    )
    """)

    con.commit()
    con.close()

crear_tabla()


@app.route("/")
def inicio():

    con = conectar()
    cur = con.cursor()

    cur.execute("""
    SELECT * FROM tareas
    ORDER BY completada ASC, fecha ASC
    """)

    tareas = cur.fetchall()

    completadas = 0
    pendientes = 0
    urgentes = 0

    hoy = datetime.now().date()

    for tarea in tareas:

        if tarea[3] == 1:
            completadas += 1
        else:
            pendientes += 1

        if tarea[2] and tarea[3] == 0:

            fecha = datetime.strptime(tarea[2], "%Y-%m-%d").date()

            if (fecha - hoy).days <= 1:
                urgentes += 1

    proxima = None

    for tarea in tareas:
        if tarea[3] == 0:
            proxima = tarea
            break

    con.close()

    return render_template(
        "index.html",
        tareas=tareas,
        completadas=completadas,
        pendientes=pendientes,
        urgentes=urgentes,
        proxima=proxima
    )


@app.route("/agregar", methods=["POST"])
def agregar():

    titulo = request.form["titulo"]
    fecha = request.form["fecha"]

    if titulo.strip() == "":
        return redirect("/?error=1")

    con = conectar()
    cur = con.cursor()

    cur.execute(
        "INSERT INTO tareas (titulo, fecha, completada) VALUES (?, ?, 0)",
        (titulo, fecha)
    )

    con.commit()
    con.close()

    return redirect("/")


@app.route("/completar/<id>")
def completar(id):

    con = conectar()
    cur = con.cursor()

    cur.execute("UPDATE tareas SET completada=1 WHERE id=?", (id,))

    con.commit()
    con.close()

    return redirect("/")


@app.route("/eliminar/<id>")
def eliminar(id):

    con = conectar()
    cur = con.cursor()

    cur.execute("DELETE FROM tareas WHERE id=?", (id,))

    con.commit()
    con.close()

    return redirect("/")


app.run(debug=True)