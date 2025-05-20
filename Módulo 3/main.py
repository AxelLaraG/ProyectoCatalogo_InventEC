import tkinter as tk
from tkinter import messagebox, Toplevel
from pymongo import MongoClient
import bcrypt
import subprocess
import sys
import os

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
                self._users["admin"] = {"username": "admin", "password_hash": hashed}
            except Exception as bcrypt_e: print(f"Error mock bcrypt: {bcrypt_e}")
        def find_one(self, query):
            user = self._users.get(query.get("username"))
            return dict(user) if user else None
        def insert_one(self, document):
            username = document.get("username")
            if username in self._users: raise Exception(f"MockDB: User '{username}' already exists.") 
            self._users[username] = document
            class InsertOneResult: __init__ = lambda self, inserted_id: setattr(self, 'inserted_id', inserted_id)
            return InsertOneResult(username)
    users_collection = MockUsersCollection()
    print("Usando colección SIMULADA (fallback) debido a error de conexión con MongoDB.")
    USANDO_BD_SIMULADA = True

def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password_from_db):
    """Verifies a plain password against a hashed password from the DB."""
    if not isinstance(hashed_password_from_db, bytes):
        if isinstance(hashed_password_from_db, str) and hashed_password_from_db.startswith("b'") :
            try:
                import ast
                hashed_password_from_db = ast.literal_eval(hashed_password_from_db)
            except: pass
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_from_db)

def login_user():
    """Handles the login process and redirige si es exitoso."""
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error de Login", "Usuario y contraseña son requeridos.")
        return

    try:
        user_data = users_collection.find_one({"username": username})

        if user_data and 'password_hash' in user_data:
            if verify_password(password, user_data['password_hash']):
                messagebox.showinfo("Login Exitoso", f"Bienvenido, {username}!\nSerás redirigido.")
                
                login_window.destroy()
                
                directorio_actual = os.path.dirname(os.path.abspath(__file__))
                
                ruta_carpeta_externa = "RUTA ABSOLUTA DE LA CARPETA" 
                nombre_script_externo = "nombre_deL_script.py"

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
                messagebox.showerror("Error de Login", "Usuario o contraseña incorrectos.")
        else:
            messagebox.showerror("Error de Login", "Usuario o contraseña incorrectos.")

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error durante el login: {e}")
        print(f"Error de login: {e}")

def open_registration_window():
    """Opens the registration window."""
    global entry_reg_username, entry_reg_password, entry_reg_confirm_password, registration_window
    registration_window = Toplevel(login_window)
    registration_window.title("Registrar Nuevo Usuario")
    registration_window.geometry("400x250")
    registration_window.resizable(False, False)
    
    login_x = login_window.winfo_x(); login_y = login_window.winfo_y()
    login_width = login_window.winfo_width(); login_height = login_window.winfo_height()
    reg_width = 400; reg_height = 250
    reg_x = login_x + (login_width // 2) - (reg_width // 2)
    reg_y = login_y + (login_height // 2) - (reg_height // 2)
    registration_window.geometry(f'{reg_width}x{reg_height}+{reg_x}+{reg_y}')
    
    reg_frame = tk.Frame(registration_window, padx=20, pady=20); reg_frame.pack(expand=True, fill="both")
    
    tk.Label(reg_frame, text="Nuevo Usuario:").grid(row=0, column=0, sticky="w", pady=(0,5))
    entry_reg_username = tk.Entry(reg_frame, width=35); entry_reg_username.grid(row=0, column=1, pady=(0,5))
    
    tk.Label(reg_frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=(0,5))
    entry_reg_password = tk.Entry(reg_frame, show="*", width=35); entry_reg_password.grid(row=1, column=1, pady=(0,5))
    
    tk.Label(reg_frame, text="Confirmar Contraseña:").grid(row=2, column=0, sticky="w", pady=(0,10))
    entry_reg_confirm_password = tk.Entry(reg_frame, show="*", width=35); entry_reg_confirm_password.grid(row=2, column=1, pady=(0,10))
    
    btn_submit_registration = tk.Button(reg_frame, text="Registrar", command=register_new_user, width=15)
    btn_submit_registration.grid(row=3, column=0, columnspan=2, pady=(5,0))
    
    registration_window.transient(login_window); registration_window.grab_set(); login_window.wait_window(registration_window)

def register_new_user():
    """Handles the new user registration process."""
    username = entry_reg_username.get(); password = entry_reg_password.get(); confirm_password = entry_reg_confirm_password.get()
    if not username or not password or not confirm_password:
        messagebox.showerror("Error de Registro", "Todos los campos son requeridos.", parent=registration_window); return
    if password != confirm_password:
        messagebox.showerror("Error de Registro", "Las contraseñas no coinciden.", parent=registration_window); return
    if len(password) < 6:
        messagebox.showerror("Error de Registro", "La contraseña debe tener al menos 6 caracteres.", parent=registration_window); return
    try:
        if users_collection.find_one({"username": username}):
            messagebox.showerror("Error de Registro", "El nombre de usuario ya existe.", parent=registration_window); return
        
        hashed_pass = hash_password(password)
        insert_result = users_collection.insert_one({"username": username, "password_hash": hashed_pass})
        
        if USANDO_BD_SIMULADA or (hasattr(insert_result, 'inserted_id') and insert_result.inserted_id):
            messagebox.showinfo("Registro Exitoso", "Usuario registrado exitosamente.", parent=registration_window)
            registration_window.destroy()
        else: 
            messagebox.showerror("Error de Registro", "No se pudo registrar el usuario.", parent=registration_window)
    except Exception as e:
        if "User already exists" in str(e) or "E11000" in str(e): 
            messagebox.showerror("Error de Registro", "El nombre de usuario ya existe.", parent=registration_window)
        else: 
            messagebox.showerror("Error de Registro", f"Ocurrió un error: {e}", parent=registration_window)
        print(f"Error de registro: {e}")

login_window = tk.Tk()
login_window.title("Login - Catálogo Digital")
login_window.geometry("350x250")
login_window.resizable(False, False)

window_width = 350; window_height = 250
screen_width = login_window.winfo_screenwidth(); screen_height = login_window.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2); center_y = int(screen_height/2 - window_height / 2)
login_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

main_frame = tk.Frame(login_window, padx=20, pady=20); main_frame.pack(expand=True, fill="both")

lbl_username = tk.Label(main_frame, text="Usuario:"); lbl_username.grid(row=0, column=0, sticky="w", pady=(0, 5))
entry_username = tk.Entry(main_frame, width=30); entry_username.grid(row=0, column=1, pady=(0, 5))

lbl_password = tk.Label(main_frame, text="Contraseña:"); lbl_password.grid(row=1, column=0, sticky="w", pady=(0, 10))
entry_password = tk.Entry(main_frame, show="*", width=30); entry_password.grid(row=1, column=1, pady=(0, 10))

btn_login = tk.Button(main_frame, text="Ingresar", command=login_user, width=15); btn_login.grid(row=2, column=0, columnspan=2, pady=(5,5))
btn_register_prompt = tk.Button(main_frame, text="Registrarse", command=open_registration_window, width=15)
btn_register_prompt.grid(row=3, column=0, columnspan=2, pady=(5,0))

login_window.mainloop()