# Descomprime cafeteria_utec.zip, instala web.py y corre el servidor.
# Uso: pon este archivo junto al .zip y ejecuta:  python instalar.py
import os, subprocess, sys, zipfile

aqui = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(aqui, 'cafeteria_utec.zip')

print('1) Descomprimiendo...')
with zipfile.ZipFile(zip_path) as z:
    z.extractall(aqui)

carpeta = os.path.join(aqui, 'cafeteria_utec')

print('2) Instalando dependencias (web.py)...')
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',
                       os.path.join(carpeta, 'requirements.txt')])

print('3) Iniciando servidor en http://localhost:8080  (Ctrl+C para parar)')
os.chdir(carpeta)
subprocess.call([sys.executable, 'app.py'])
