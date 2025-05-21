import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from pymongo import MongoClient
import bcrypt
import subprocess
import sys
import os
import ast
import datetime
import re

try:
    client = MongoClient('mongodb+srv://axmadlar:pw1234@cluster0.rrnubrd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['proyecto']
    users_collection = db['usuarios']
    print("¡Conexión exitosa a MongoDB Atlas!")
    USANDO_BD_SIMULADA = False
except Exception as e:
    print(f"No se pudo conectar a MongoDB Atlas: {e}")
    messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a MongoDB: {e}\nLa aplicación usará un modo de demostración.")
    
    class MockUsersCollection:
        _users = {}
        def __init__(self):
            try:
                password_plain = "adminpass"
                hashed = bcrypt.hashpw(password_plain.encode('utf-8'), bcrypt.gensalt())
                self._users["admin@example.com"] = {
                    "email": "admin@example.com", 
                    "password_hash": hashed, 
                    "nombre": "Admin", 
                    "apellidos": "User",
                    "autorizado_para_prestamos": True,
                    "terminos_aceptados": True,
                    "privacidad_aceptada": True,
                    "fecha_registro": datetime.datetime.utcnow(),
                    "telefono": "",
                }
            except Exception as bcrypt_e: print(f"Error mock bcrypt: {bcrypt_e}")
        
        def find_one(self, query):
            user = self._users.get(query.get("email"))
            return dict(user) if user else None
        
        def insert_one(self, document):
            email = document.get("email")
            if email in self._users:
                raise Exception(f"MockDB: E11000 duplicate key error collection: demo.usuarios index: email_1 dup key: {{ email: \"{email}\" }}")
            self._users[email] = document
            class InsertOneResult:
                def __init__(self, inserted_id):
                    self.inserted_id = inserted_id
            return InsertOneResult(email)

    users_collection = MockUsersCollection()
    print("Usando colección SIMULADA (fallback) debido a error de conexión con MongoDB.")
    USANDO_BD_SIMULADA = True

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password_from_db):
    if not isinstance(hashed_password_from_db, bytes):
        if isinstance(hashed_password_from_db, str) and hashed_password_from_db.startswith("b'") :
            try:
                hashed_password_from_db = ast.literal_eval(hashed_password_from_db)
            except: 
                pass 
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_from_db)

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

def is_valid_password(password):
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe contener al menos un número."
    return True, ""

def is_valid_name_component(name_component):
    if not name_component.strip():
        return False
    regex = r"^[a-zA-ZÀ-ÿ\s'-]+$"
    if not re.fullmatch(regex, name_component):
        return False
    if name_component.isdigit():
        return False
    return True

def is_valid_mexican_phone(phone_str):
    if not phone_str:
        return True
    cleaned_phone = re.sub(r'[\s-]', '', phone_str)
    return cleaned_phone.isdigit() and len(cleaned_phone) == 10


def login_user():
    email = entry_email_login.get()
    password = entry_password_login.get()

    if not email or not password:
        messagebox.showerror("Error de Login", "Correo electrónico y contraseña son requeridos.")
        return

    if not is_valid_email(email):
        messagebox.showerror("Error de Login", "Formato de correo electrónico inválido.")
        entry_email_login.focus_set()
        return

    try:
        user_data = users_collection.find_one({"email": email})

        if user_data and 'password_hash' in user_data:
            if verify_password(password, user_data['password_hash']):
                nombre_usuario = user_data.get("nombre", email)
                messagebox.showinfo("Login Exitoso", f"Bienvenido, {nombre_usuario}!\nSerás redirigido.")
                
                login_window.destroy()
                
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                
                ruta_carpeta_externa = "./" 
                nombre_script_externo = "menu.py"

                ruta_completa_script = os.path.join(ruta_carpeta_externa, nombre_script_externo)
                ruta_absoluta_script_externo = os.path.abspath(ruta_completa_script)

                print(f"Intentando ejecutar: {ruta_absoluta_script_externo}")

                if os.path.exists(ruta_absoluta_script_externo) and ruta_absoluta_script_externo.endswith(".py"):
                    try:
                        subprocess.Popen([sys.executable, ruta_absoluta_script_externo])
                        print(f"Script '{nombre_script_externo}' lanzado exitosamente.")
                    except Exception as e_exec:
                        messagebox.showerror("Error de Redirección", f"No se pudo ejecutar el script externo:\n{e_exec}")
                        print(f"Error al ejecutar script externo '{ruta_absoluta_script_externo}': {e_exec}")
                else:
                    messagebox.showerror("Error de Redirección", f"No se encontró el script externo en:\n{ruta_absoluta_script_externo}\n\nVerifica la ruta configurada en el código.")
                    print(f"Script externo no encontrado: {ruta_absoluta_script_externo}")
                
                return
            else:
                messagebox.showerror("Error de Login", "Correo electrónico o contraseña incorrectos.")
        else:
            messagebox.showerror("Error de Login", "Correo electrónico o contraseña incorrectos.")
        entry_email_login.focus_set()

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante el login: {e}")
        print(f"Error de login: {e}")

def open_registration_window():
    global entry_reg_nombre, entry_reg_apellidos, entry_reg_email, entry_reg_password
    global entry_reg_confirm_password, entry_reg_telefono, entry_reg_cargo
    global var_experiencia, var_terminos, var_privacidad, registration_window

    registration_window = Toplevel(login_window)
    registration_window.title("Registrar Nuevo Usuario")
    registration_window.geometry("500x520") 
    registration_window.resizable(False, False)
    
    login_x = login_window.winfo_x(); login_y = login_window.winfo_y()
    login_width = login_window.winfo_width(); login_height = login_window.winfo_height()
    reg_width = 500; reg_height = 520
    reg_x = login_x + (login_width // 2) - (reg_width // 2)
    reg_y = login_y + (login_height // 2) - (reg_height // 2)
    registration_window.geometry(f'{reg_width}x{reg_height}+{reg_x}+{reg_y}')
    
    reg_frame = tk.Frame(registration_window, padx=20, pady=20); reg_frame.pack(expand=True, fill="both")
    
    current_row = 0
    tk.Label(reg_frame, text="Nombre(s):*").grid(row=current_row, column=0, sticky="w", pady=(0,5))
    entry_reg_nombre = tk.Entry(reg_frame, width=40); entry_reg_nombre.grid(row=current_row, column=1, pady=(0,5))
    current_row += 1

    tk.Label(reg_frame, text="Apellidos:*").grid(row=current_row, column=0, sticky="w", pady=(0,5))
    entry_reg_apellidos = tk.Entry(reg_frame, width=40); entry_reg_apellidos.grid(row=current_row, column=1, pady=(0,5))
    current_row += 1

    tk.Label(reg_frame, text="Correo Electrónico:*").grid(row=current_row, column=0, sticky="w", pady=(0,5))
    entry_reg_email = tk.Entry(reg_frame, width=40); entry_reg_email.grid(row=current_row, column=1, pady=(0,5))
    current_row += 1
    
    tk.Label(reg_frame, text="Contraseña:*").grid(row=current_row, column=0, sticky="w", pady=(0,5))
    entry_reg_password = tk.Entry(reg_frame, show="*", width=40); entry_reg_password.grid(row=current_row, column=1, pady=(0,5))
    current_row += 1
    
    tk.Label(reg_frame, text="Confirmar Contraseña:*").grid(row=current_row, column=0, sticky="w", pady=(0,10))
    entry_reg_confirm_password = tk.Entry(reg_frame, show="*", width=40); entry_reg_confirm_password.grid(row=current_row, column=1, pady=(0,10))
    current_row += 1

    tk.Label(reg_frame, text="Teléfono (10 dígitos, opcional):").grid(row=current_row, column=0, sticky="w", pady=(0,5))
    entry_reg_telefono = tk.Entry(reg_frame, width=40); entry_reg_telefono.grid(row=current_row, column=1, pady=(0,5))
    current_row += 1
    
    var_terminos = tk.BooleanVar()
    chk_terminos = tk.Checkbutton(reg_frame, text="Acepto los Términos y Condiciones de Uso*", variable=var_terminos)
    chk_terminos.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(5,0))
    current_row += 1

    var_privacidad = tk.BooleanVar()
    chk_privacidad = tk.Checkbutton(reg_frame, text="He leído y acepto la Política de Privacidad*", variable=var_privacidad)
    chk_privacidad.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(0,10))
    current_row += 1

    tk.Label(reg_frame, text="* Campos obligatorios").grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(5,0))
    current_row +=1

    btn_submit_registration = tk.Button(reg_frame, text="Registrar", command=register_new_user, width=15)
    btn_submit_registration.grid(row=current_row, column=0, columnspan=2, pady=(10,0))
    
    registration_window.transient(login_window); registration_window.grab_set(); login_window.wait_window(registration_window)

def register_new_user():
    nombre = entry_reg_nombre.get()
    apellidos = entry_reg_apellidos.get()
    email = entry_reg_email.get() 
    password = entry_reg_password.get()
    confirm_password = entry_reg_confirm_password.get()
    telefono = entry_reg_telefono.get()
    acepta_terminos = var_terminos.get()
    acepta_privacidad = var_privacidad.get()

    if not nombre.strip():
        messagebox.showerror("Error de Registro", "El campo Nombre(s) es requerido.", parent=registration_window)
        entry_reg_nombre.focus_set()
        return
    if not is_valid_name_component(nombre):
        messagebox.showerror("Error de Registro", "Nombre(s) inválido. Use solo letras, espacios, apóstrofes o guiones.", parent=registration_window)
        entry_reg_nombre.focus_set()
        return
    
    if not apellidos.strip():
        messagebox.showerror("Error de Registro", "El campo Apellidos es requerido.", parent=registration_window)
        entry_reg_apellidos.focus_set()
        return
    if not is_valid_name_component(apellidos):
        messagebox.showerror("Error de Registro", "Apellidos inválidos. Use solo letras, espacios, apóstrofes o guiones.", parent=registration_window)
        entry_reg_apellidos.focus_set()
        return

    if not email.strip():
        messagebox.showerror("Error de Registro", "El campo Correo Electrónico es requerido.", parent=registration_window)
        entry_reg_email.focus_set()
        return
    if not is_valid_email(email):
        messagebox.showerror("Error de Registro", "Formato de correo electrónico inválido.", parent=registration_window)
        entry_reg_email.focus_set()
        return
    
    valid_pass, pass_error_msg = is_valid_password(password)
    if not valid_pass:
        messagebox.showerror("Error de Registro", pass_error_msg, parent=registration_window)
        entry_reg_password.focus_set()
        return
        
    if password != confirm_password:
        messagebox.showerror("Error de Registro", "Las contraseñas no coinciden.", parent=registration_window)
        entry_reg_confirm_password.focus_set()
        return

    if telefono.strip() and not is_valid_mexican_phone(telefono):
        messagebox.showerror("Error de Registro", "Número de teléfono inválido. Debe contener 10 dígitos numéricos (opcionalmente con espacios o guiones).", parent=registration_window)
        entry_reg_telefono.focus_set()
        return
        
    if not acepta_terminos:
        messagebox.showerror("Error de Registro", "Debe aceptar los Términos y Condiciones.", parent=registration_window)
        return
    if not acepta_privacidad:
        messagebox.showerror("Error de Registro", "Debe aceptar la Política de Privacidad.", parent=registration_window)
        return

    try:
        if users_collection.find_one({"email": email}):
            messagebox.showerror("Error de Registro", "El correo electrónico ya está registrado.", parent=registration_window)
            entry_reg_email.focus_set()
            return
        
        hashed_pass = hash_password(password)
        cleaned_telefono = re.sub(r'[\s-]', '', telefono) if telefono.strip() else None
        
        user_document = {
            "nombre": nombre.strip(),
            "apellidos": apellidos.strip(),
            "email": email.strip(), 
            "password_hash": hashed_pass,
            "telefono": cleaned_telefono,
            "terminos_aceptados": acepta_terminos,
            "privacidad_aceptada": acepta_privacidad,
            "fecha_registro": datetime.datetime.utcnow(),
            "autorizado_para_prestamos": True 
        }
        
        insert_result = users_collection.insert_one(user_document)
        
        if USANDO_BD_SIMULADA or (hasattr(insert_result, 'inserted_id') and insert_result.inserted_id):
            messagebox.showinfo("Registro Exitoso", "Usuario registrado exitosamente como autorizado para préstamos.", parent=registration_window)
            registration_window.destroy()
        else: 
            messagebox.showerror("Error de Registro", "No se pudo registrar el usuario.", parent=registration_window)

    except Exception as e:
        if "E11000" in str(e) or "User already exists" in str(e) or "email_1 dup key" in str(e): 
            messagebox.showerror("Error de Registro", "El correo electrónico ya está registrado.", parent=registration_window)
        else: 
            messagebox.showerror("Error de Registro", f"Ocurrió un error: {e}", parent=registration_window)
        print(f"Error de registro: {e}")


login_window = tk.Tk()
login_window.title("Login - Catálogo Digital y Préstamos")
login_window.geometry("350x250") 
login_window.resizable(False, False)

window_width = 350; window_height = 250
screen_width = login_window.winfo_screenwidth(); screen_height = login_window.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2); center_y = int(screen_height/2 - window_height / 2)
login_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

main_frame = tk.Frame(login_window, padx=20, pady=20); main_frame.pack(expand=True, fill="both")

lbl_email_login = tk.Label(main_frame, text="Correo Electrónico:"); lbl_email_login.grid(row=0, column=0, sticky="w", pady=(0, 5))
entry_email_login = tk.Entry(main_frame, width=30); entry_email_login.grid(row=0, column=1, pady=(0, 5)) 

lbl_password_login = tk.Label(main_frame, text="Contraseña:"); lbl_password_login.grid(row=1, column=0, sticky="w", pady=(0, 10))
entry_password_login = tk.Entry(main_frame, show="*", width=30); entry_password_login.grid(row=1, column=1, pady=(0, 10)) 

btn_login = tk.Button(main_frame, text="Ingresar", command=login_user, width=15); btn_login.grid(row=2, column=0, columnspan=2, pady=(5,5))
btn_register_prompt = tk.Button(main_frame, text="Registrarse", command=open_registration_window, width=15)
btn_register_prompt.grid(row=3, column=0, columnspan=2, pady=(5,0))

login_window.mainloop()