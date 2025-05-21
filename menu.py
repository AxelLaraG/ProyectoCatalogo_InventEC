import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import sys
import time

modulos_procesos_activos = {}

def obtener_ruta_base():
    return os.path.dirname(os.path.abspath(__file__))

def lanzar_modulo(nombre_carpeta_modulo, nombre_script_modulo):
    global modulos_procesos_activos

    identificador_modulo = f"{nombre_carpeta_modulo}/{nombre_script_modulo}"
    python_executable = sys.executable
    ruta_base = obtener_ruta_base()
    ruta_script_modulo = os.path.join(ruta_base, nombre_carpeta_modulo, nombre_script_modulo)

    if identificador_modulo in modulos_procesos_activos:
        proceso_existente = modulos_procesos_activos[identificador_modulo]
        if proceso_existente.poll() is None:
            messagebox.showinfo("Módulo en Ejecución",
                                f"El módulo '{nombre_script_modulo}' ya está abierto.")
            return
        else:
            del modulos_procesos_activos[identificador_modulo]

    if not os.path.exists(ruta_script_modulo):
        messagebox.showerror("Error de Módulo", f"No se encontró el script del módulo:\n{ruta_script_modulo}")
        print(f"No se encontró: {ruta_script_modulo}")
        return

    try:
        nuevo_proceso = subprocess.Popen([python_executable, ruta_script_modulo])
        modulos_procesos_activos[identificador_modulo] = nuevo_proceso
        print(f"Lanzando: {ruta_script_modulo} (PID: {nuevo_proceso.pid})")
    except Exception as e:
        messagebox.showerror("Error al lanzar módulo",
                             f"No se pudo iniciar el módulo {nombre_script_modulo}.\nError: {e}")
        print(f"Error al lanzar {ruta_script_modulo}: {e}")

def cerrar_modulos_lanzar_y_cerrar_ventana(ventana_a_cerrar, nombre_carpeta_script_principal, nombre_script_principal):
    global modulos_procesos_activos

    print("Intentando cerrar todos los módulos activos...")
    identificadores_a_eliminar = []
    for identificador, proceso in list(modulos_procesos_activos.items()):
        if proceso.poll() is None:
            try:
                print(f"Enviando señal de terminación al módulo: {identificador} (PID: {proceso.pid})")
                proceso.terminate()
            except subprocess.TimeoutExpired:
                print(f"Módulo {identificador} no terminó a tiempo. Considerar forzar (kill) si es necesario.")
            except Exception as e:
                print(f"Error al intentar terminar el módulo {identificador}: {e}")
        identificadores_a_eliminar.append(identificador)

    if identificadores_a_eliminar:
        time.sleep(0.5)

    for identificador in identificadores_a_eliminar:
        if identificador in modulos_procesos_activos:
            proceso = modulos_procesos_activos[identificador]
            if proceso.poll() is not None:
                 print(f"Módulo {identificador} confirmado como terminado.")
                 del modulos_procesos_activos[identificador]
            else:
                print(f"Módulo {identificador} aún podría estar activo después de la señal de terminación.")

    print(f"Módulos activos restantes en rastreo: {list(modulos_procesos_activos.keys())}")

    ruta_base = obtener_ruta_base()
    ruta_script_a_lanzar = os.path.join(ruta_base, nombre_carpeta_script_principal, nombre_script_principal)
    python_executable = sys.executable
    lanzamiento_principal_intentado = False

    if os.path.exists(ruta_script_a_lanzar):
        try:
            subprocess.Popen([python_executable, ruta_script_a_lanzar])
            print(f"Lanzando script principal {ruta_script_a_lanzar} y preparando para cerrar el menú.")
            lanzamiento_principal_intentado = True
        except Exception as e:
            messagebox.showerror("Error al lanzar script principal", f"No se pudo iniciar el script {nombre_script_principal}.\nError: {e}")
            print(f"Error al lanzar {ruta_script_a_lanzar}: {e}")
    else:
        messagebox.showerror("Error de Script Principal", f"No se encontró el script principal:\n{ruta_script_a_lanzar}")
        print(f"No se encontró: {ruta_script_a_lanzar}")

    if lanzamiento_principal_intentado:
        ventana_a_cerrar.destroy()

def crear_menu_principal_gui():
    ventana = tk.Tk()
    ventana.title("Menú Principal del Sistema de Gestión")
    ventana.geometry("550x450")

    label_titulo = tk.Label(ventana, text="Sistema de Gestión de Equipamiento", font=("Arial", 18, "bold"), pady=20)
    label_titulo.pack()

    label_subtitulo = tk.Label(ventana, text="Selecciona un módulo para ejecutar:", font=("Arial", 12), pady=10)
    label_subtitulo.pack()

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    modulos_config = [
        {"texto": "1. Búsqueda y Visualización del Catálogo", "carpeta": "Módulo 1", "script": "main.py"},
        {"texto": "2. Gestión de Equipamiento (Admin)", "carpeta": "Módulo 2", "script": "main.py"},
        {"texto": "3. Gestión de Usuarios (para préstamos)", "carpeta": "Módulo 3", "script": "main.py"},
        {"texto": "4. Gestión de Préstamos y Devoluciones", "carpeta": "Módulo 4", "script": "main.py"},
    ]

    for config in modulos_config:
        btn = tk.Button(
            frame_botones,
            text=config["texto"],
            command=lambda c=config: lanzar_modulo(c["carpeta"], c["script"]),
            width=45,
            pady=5
        )
        btn.pack(pady=5)

    btn_abrir_principal_y_salir = tk.Button(
        ventana,
        text="Salir del Menú",
        command=lambda: cerrar_modulos_lanzar_y_cerrar_ventana(ventana, ".", "main.py"),
        width=40,
        pady=5,
        bg="mediumseagreen",
        fg="white"
    )
    btn_abrir_principal_y_salir.pack(pady=20)

    ventana.mainloop()

if __name__ == "__main__":
    crear_menu_principal_gui()