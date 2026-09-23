"""
Genera la imagen del QR que la gente escaneará.

Uso:
    python generar_qr.py https://tu-app-desplegada.onrender.com

Si no pasas la URL como argumento, te la pide de forma interactiva.
Guarda el resultado como qr_nodia_descuento.png en esta misma carpeta.
"""
import sys
import qrcode


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
    else:
        url = input(
            "URL donde quedó desplegada la app (ej. https://nodia-promo.onrender.com): "
        ).strip()

    if not url.startswith("http"):
        print("Aviso: la URL no empieza con http/https — revisa que sea correcta.")

    img = qrcode.make(url)
    salida = "qr_nodia_descuento.png"
    img.save(salida)
    print(f"Listo. QR guardado como {salida}, apuntando a: {url}")
    print("Imprímelo o compártelo en el grupo tal cual.")


if __name__ == "__main__":
    main()
