import os
import sys
import argparse
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

"""
Aplicación migrada de c# que fue creada con .netcore 5.
Necesitaba una app en arch linux y me acordé que había creado una pero no tengo las librerías de netcore instaladas
Por lo que, mejor migré el código que había creado a python.
Testeado y probado, y ya utilizado ;)

"""


class Reorganizador:
    def __init__(self):
        self.args = self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Reorganizador de fotos")
        return parser.parse_args()

    def reorganiza(self, crear_carpeta, item):
        """
        Crea directorio - si no existe - en base a la fecha extraída, ya sea de
        exif o de modificación.
        """
        if not os.path.exists(crear_carpeta):
            os.makedirs(crear_carpeta)
            os.rename(item, os.path.join(crear_carpeta, os.path.basename(item)))
        elif not os.path.exists(os.path.join(crear_carpeta, os.path.basename(item))):
            os.rename(item, os.path.join(crear_carpeta, os.path.basename(item)))


    def no_hay_tag(self, fi, item):
        """
        Si no hay datos exif se toma la fecha desde la fecha de modificaciónd el archivo.
        Convertir el tiempo de modificación en una fecha legible (año, mes, día)
        Y se manda a reorganizar.
        """
        crear_carpeta = datetime.fromtimestamp(fi.st_mtime).strftime("%Y_%m_%d")
        self.reorganiza(crear_carpeta, item)

    def progreso(self, progreso, total=100):
        """
        Muestra una barra de progreso en la terminal
        """
        onechunk = 30.0 / total
        barra = "[" + "=" * int(onechunk * progreso) + " " * (30 - int(onechunk * progreso)) + "]"
        sys.stdout.write(f"\r{barra} {progreso}/{total} procesado...   ")
        sys.stdout.flush()

    def leer_fecha_exif(self, image_path):
        """
        Lee la fecha desde los datos exif del archivo, si es que está presente.
        """
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            for tag, value in (exif_data or {}).items():
                if TAGS.get(tag) == "DateTime":
                    return value.replace(":", "_").split(" ")[0]
        except Exception as e:
            print(f"No se pudo leer EXIF de {image_path}: {e}")
        return None

    def main(self):
        """
        Programa "principal"
        """
        print("Reorganizador de fotos")
        print("Más información en: https://github.com/fotosycaptura/py-reorganizador")

        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        inicio = 1
        termino = len(files)

        for item in files:
            fi = os.stat(item)
            self.progreso(inicio, termino)

            extension = os.path.splitext(item)[1].lower()
            if extension in [".cr2", ".nef", ".jpg"]:
                fecha_exif = self.leer_fecha_exif(item)
                if fecha_exif:
                    self.reorganiza(fecha_exif, item)
                else:
                    self.no_hay_tag(fi, item)

            inicio += 1
        self.progreso(termino, termino)
        print("\n... Finalizado.")

if __name__ == "__main__":
    reorganizador = Reorganizador()
    reorganizador.main()
