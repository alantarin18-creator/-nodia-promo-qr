# NODIA — Generador de códigos de descuento por QR

Al escanear el QR, cada persona llega a una página que le entrega un
código único (nunca repetido) con 75% de descuento en el Programa Total
de Digitalización. Los códigos se guardan en SQLite (`codigos.db`, se
crea solo al arrancar la app).

## Cómo funciona

- `GET /` — genera un código nuevo de 6 caracteres y lo guarda. Si la
  misma persona (mismo navegador/teléfono) vuelve a entrar, ve **el
  mismo código** que ya tenía, no uno nuevo — evita que alguien refresque
  la página y acumule códigos.
- `GET /admin/codigos` — lista todos los códigos generados hasta ahora,
  para que lleves control manual de canjes. No tiene contraseña: si
  despliegas esto públicamente, no compartas esa URL, o agrégale
  autenticación si te importa que nadie más la vea.

**Límite conocido:** el control de "una persona = un código" es por
cookie, no por identidad real. Alguien con ganas de sacar más de un
código puede hacerlo en modo incógnito o borrando cookies. Para un
grupo/evento informal es suficiente; si más adelante quieres que sea a
prueba de trampas, la solución es pedir un teléfono o correo antes de
generar el código (puedo agregarlo si te hace falta).

## Correrlo en tu computadora

```bash
pip install -r requirements.txt
python app.py
```

Ábrelo en `http://localhost:5000`. Cada vez que entres desde el mismo
navegador verás tu mismo código; usa modo incógnito para simular que
eres "otra persona" y confirmar que sí te da uno distinto.

## Desplegarlo (para que el QR funcione desde cualquier celular)

Necesitas que quede accesible por internet. La opción más simple y
gratuita para una app Flask como esta es **Render**:

1. Sube esta carpeta a un repo de GitHub.
2. En [render.com](https://render.com), crea un "Web Service" nuevo
   apuntando a ese repo.
3. Build command: `pip install -r requirements.txt`
   Start command: `gunicorn app:app`
4. Despliega. Render te da una URL tipo
   `https://tu-servicio.onrender.com`.

Alternativas equivalentes: Railway o Fly.io. Si prefieres quedarte en
tu stack actual (Vercel + Supabase, igual que NODIA), dímelo y te
adapto esto a una API route de Next.js con una tabla en Supabase en
vez de SQLite — la lógica es la misma, solo cambia dónde vive.

## Generar el QR

Una vez que tengas la URL desplegada:

```bash
python generar_qr.py https://tu-servicio.onrender.com
```

Esto guarda `qr_nodia_descuento.png` — imprímelo o compártelo tal cual
en el grupo.

## Ajustar el texto del descuento

Edita las constantes al inicio de `app.py`:

```python
DESCUENTO = "75%"
PROGRAMA = "Programa Total de Digitalización — NODIA"
```
