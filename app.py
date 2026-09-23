"""
NODIA — Generador de códigos de descuento por QR
--------------------------------------------------
Al escanear el QR, cada persona cae en la ruta "/" y recibe un código
alfanumérico único (nunca repetido) con el 75% de descuento en el
Programa Total de Digitalización. El código se guarda en SQLite.

Control "una persona = un código": se usa una cookie en el navegador.
Si la misma persona vuelve a escanear desde el mismo teléfono/navegador,
ve SU MISMO código (no uno nuevo). Esto no es a prueba de abuso (alguien
podría usar modo incógnito o borrar cookies para sacar otro código), pero
es suficiente para un evento/grupo informal. Si más adelante necesitas
control estricto, la solución real es pedir un dato (teléfono o correo)
antes de generar el código.
"""
import os
import random
import sqlite3
from datetime import datetime, timezone

from flask import Flask, render_template, make_response, request

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "codigos.db")

# ----------------------------------------------------------------------
# Configuración — ajusta aquí el texto del descuento/programa
# ----------------------------------------------------------------------
DESCUENTO = "75%"
PROGRAMA = "Programa Total de Digitalización — NODIA"
COOKIE_NAME = "nodia_codigo"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 año

# Alfabeto sin caracteres que se confunden a simple vista (0/O, 1/I/L)
ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LARGO_CODIGO = 6
# Espacio de códigos posibles: 32^6 ≈ 1,073 millones de combinaciones.
# Para un grupo de cualquier tamaño realista, las colisiones son
# prácticamente imposibles; aun así el código valida unicidad contra la
# base de datos antes de entregar cada código.


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS codigos (
            codigo TEXT PRIMARY KEY,
            generado_en TEXT NOT NULL,
            redimido INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def generar_codigo_unico() -> str:
    conn = get_db()
    try:
        while True:
            codigo = "".join(random.choices(ALFABETO, k=LARGO_CODIGO))
            existe = conn.execute(
                "SELECT 1 FROM codigos WHERE codigo = ?", (codigo,)
            ).fetchone()
            if existe:
                continue  # colisión (extremadamente improbable) -> reintenta
            conn.execute(
                "INSERT INTO codigos (codigo, generado_en) VALUES (?, ?)",
                (codigo, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
            return codigo
    finally:
        conn.close()


@app.route("/")
def generar():
    # ¿Esta persona ya tiene un código (misma cookie)?
    codigo_existente = request.cookies.get(COOKIE_NAME)
    if codigo_existente:
        conn = get_db()
        fila = conn.execute(
            "SELECT codigo FROM codigos WHERE codigo = ?", (codigo_existente,)
        ).fetchone()
        conn.close()
        if fila:
            return render_template(
                "codigo.html",
                codigo=codigo_existente,
                descuento=DESCUENTO,
                programa=PROGRAMA,
                repetido=True,
            )

    codigo = generar_codigo_unico()
    resp = make_response(
        render_template(
            "codigo.html",
            codigo=codigo,
            descuento=DESCUENTO,
            programa=PROGRAMA,
            repetido=False,
        )
    )
    resp.set_cookie(COOKIE_NAME, codigo, max_age=COOKIE_MAX_AGE)
    return resp


@app.route("/admin/codigos")
def admin_codigos():
    """Vista simple para que Alan vea cuántos códigos se han entregado.
    Sin autenticación: si la despliegas públicamente, considera protegerla
    o simplemente no compartir esta URL."""
    conn = get_db()
    filas = conn.execute(
        "SELECT codigo, generado_en, redimido FROM codigos ORDER BY generado_en DESC"
    ).fetchall()
    conn.close()
    return render_template("admin.html", codigos=filas, total=len(filas))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
