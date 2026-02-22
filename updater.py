import pandas as pd
import os
import re
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

    try:
        df = pd.read_csv(CSV_FILE, sep='|', dtype={'Fecha': str})
    except Exception as e:
        print(f"[-] Error al leer el CSV: {e}")
        return

    # 2. Obtener fecha de hoy
    hoy = datetime.now().strftime('%Y%m%d')
    
    # 3. Determinar la contraseña actual (la que debería estar en el código)
    # y la nueva (la que toca poner hoy)
    df = df.sort_values(by='Fecha')
    
    idx_hoy = df.index[df['Fecha'] == hoy].tolist()
    
    if not idx_hoy:
        print(f"[!] No hay cambios programados para hoy ({hoy}).")
        return

    nueva_password = df.loc[idx_hoy[0], 'Contraseña'].strip()
    
    # Intentamos buscar la contraseña anterior en el CSV para saber qué reemplazar
    current_idx = idx_hoy[0]
    if current_idx > 0:
        vieja_password = df.iloc[current_idx - 1]['Contraseña'].strip()
    else:
        vieja_password = INITIAL_PASSWORD

    if vieja_password == nueva_password:
        print("[!] La contraseña actual y la nueva son iguales. Nada que hacer.")
        return

    print(f"[*] Iniciando cambio: '{vieja_password}' -> '{nueva_password}'")

    # 4. Escanear y reemplazar en los archivos de la carpeta
    archivos_modificados = 0
    for archivo in os.listdir('.'):
        if any(archivo.endswith(ext) for ext in EXTENSIONS_TO_SEARCH):
            if archivo == 'updater.py': continue # No modificarse a sí mismo
            
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                if vieja_password in contenido:
                    nuevo_contenido = contenido.replace(vieja_password, nueva_password)
                    
                    with open(archivo, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)
                    
                    print(f"[+] Actualizado: {archivo}")
                    archivos_modificados += 1
                else:
                    # Opcional: Si no encuentra la vieja_password, podrías usar Regex 
                    # para buscar patrones como: password = "..."
                    pass
            except Exception as e:
                print(f"[-] Error procesando {archivo}: {e}")

    if archivos_modificados > 0:
        print(f"[OK] Proceso terminado. Se actualizaron {archivos_modificados} archivos.")
    else:
        print("[?] No se encontró la contraseña antigua en ningún archivo. Verifica que coincida con el CSV.")

if __name__ == "__main__":
    update_password()