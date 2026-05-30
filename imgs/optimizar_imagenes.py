"""
OPTIMIZADOR DE IMÁGENES OMAHA
==============================
Convierte todas las imágenes de una carpeta a:
  - 800x800px
  - 72 DPI
  - JPG calidad 80%
  - Fondo blanco (para imágenes con transparencia)

Uso:
  python3 optimizar_imagenes.py

Requiere:
  pip3 install Pillow

Resultado:
  - Carpeta "optimizadas/" con todas las imágenes procesadas
  - Los archivos originales no se modifican
"""

from PIL import Image
from pathlib import Path
import os

CARPETA_ORIGEN  = "."          # carpeta actual
CARPETA_DESTINO = "optimizadas"
TAMAÑO          = (800, 800)
DPI             = (72, 72)
CALIDAD         = 80
EXTENSIONES     = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp'}


def optimizar(path_origen, path_destino):
    img = Image.open(path_origen)

    # Convertir a RGB (por si tiene transparencia o es CMYK)
    if img.mode in ('RGBA', 'LA', 'P'):
        fondo = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        fondo.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = fondo
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Redimensionar manteniendo proporción con padding blanco
    img.thumbnail(TAMAÑO, Image.LANCZOS)
    fondo = Image.new('RGB', TAMAÑO, (255, 255, 255))
    offset = ((TAMAÑO[0] - img.width) // 2, (TAMAÑO[1] - img.height) // 2)
    fondo.paste(img, offset)

    # Guardar como JPG
    fondo.save(path_destino, 'JPEG', quality=CALIDAD, dpi=DPI, optimize=True)


def main():
    origen  = Path(CARPETA_ORIGEN)
    destino = Path(CARPETA_DESTINO)
    destino.mkdir(exist_ok=True)

    imagenes = [f for f in origen.iterdir()
                if f.is_file() and f.suffix.lower() in EXTENSIONES]

    if not imagenes:
        print("No se encontraron imágenes en la carpeta.")
        return

    print(f"\nOptimizando {len(imagenes)} imágenes → {CARPETA_DESTINO}/")
    print(f"Tamaño: {TAMAÑO[0]}x{TAMAÑO[1]}px | DPI: {DPI[0]} | Calidad: {CALIDAD}%\n")

    ok = 0
    errores = []

    for img_path in sorted(imagenes):
        # Nombre de salida siempre .jpg
        nombre_salida = img_path.stem + '.jpg'
        destino_path  = destino / nombre_salida

        try:
            optimizar(img_path, destino_path)
            size_kb = destino_path.stat().st_size // 1024
            print(f"  ✓  {img_path.name:<35} → {nombre_salida}  ({size_kb} KB)")
            ok += 1
        except Exception as e:
            print(f"  ✗  {img_path.name:<35} ERROR: {e}")
            errores.append(img_path.name)

    print(f"\n  Procesadas: {ok}/{len(imagenes)}")
    if errores:
        print(f"  Errores: {', '.join(errores)}")
    print(f"  Carpeta de salida: {destino.resolve()}\n")


if __name__ == "__main__":
    main()
