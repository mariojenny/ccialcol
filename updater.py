import csv
import os
from datetime import datetime

# CONFIGURACIÓN
CSV_FILE = 'psw_change.csv'
EXTENSIONS_TO_SEARCH = ['.html', '.js']  # Archivos donde podría estar la clave
INITIAL_PASSWORD = 'colombia2026'        # Clave inicial si no hay historial

def update_password():
    # 1. Cargar el CSV
    if not os.path.exists(CSV_FILE):
        print(f"[-] Error: No se encontró el archivo {CSV_FILE}")
        return

    registros = []
    # Intentar diferentes codificaciones
    encodings = ['utf-8-sig', 'latin-1', 'cp1252']
    success = False
    
    for enc in encodings:
        try:
            with open(CSV_FILE, mode='r', encoding=enc) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    clean_row = {str(k).strip(): str(v).strip() for k, v in row.items()}
                    registros.append(clean_row)
            success = True
            break
        except Exception:
            registros = []
            continue

    if not success:
        print(f"[-] Error: No se pudo leer el archivo {CSV_FILE} con ninguna codificación estándar.")
        return

    if not registros:
        print(f"[-] Error: El archivo {CSV_FILE} está vacío o no tiene el formato esperado.")
        return

    # 2. Obtener fecha de hoy
    hoy = datetime.now().strftime('%Y%m%d')
    
    # 3. Determinar la contraseña actual y la nueva
    try:
        registros.sort(key=lambda x: x['Fecha'])
    except KeyError:
        print("[-] Error: No se encontró la columna 'Fecha'. Verifique el formato del CSV.")
        return
    
    idx_hoy = -1
    for i, reg in enumerate(registros):
        if reg['Fecha'] == hoy:
            idx_hoy = i
            break
            
    if idx_hoy == -1:
        print(f"[!] No hay cambios programados para hoy ({hoy}).")
        return

    try:
        col_pass = [k for k in registros[0].keys() if 'Contrase' in k][0]
        nueva_password = registros[idx_hoy][col_pass]
        
        if idx_hoy > 0:
            vieja_password = registros[idx_hoy - 1][col_pass]
        else:
            vieja_password = INITIAL_PASSWORD
    except (IndexError, KeyError):
        print("[-] Error: No se encontró la columna de contraseña.")
        return

    if vieja_password == nueva_password:
        print("[!] La contraseña actual y la nueva son iguales. Nada que hacer.")
        return

    print(f"[*] Iniciando cambio: '{vieja_password}' -> '{nueva_password}'")

    # 4. Escanear y reemplazar en los archivos de la carpeta
    archivos_modificados = 0
    for archivo in os.listdir('.'):
        if any(archivo.endswith(ext) for ext in EXTENSIONS_TO_SEARCH):
            if archivo == 'updater.py': continue
            
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                if vieja_password in contenido:
                    nuevo_contenido = contenido.replace(vieja_password, nueva_password)
                    
                    with open(archivo, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)
                    
                    print(f"[+] Actualizado: {archivo}")
                    archivos_modificados += 1
            except Exception as e:
                print(f"[-] Error procesando {archivo}: {e}")

    if archivos_modificados > 0:
        print(f"[OK] Proceso terminado. Se actualizaron {archivos_modificados} archivos.")
    else:
        print("[?] No se encontró la contraseña antigua en ningún archivo.")

if __name__ == "__main__":
    update_password()