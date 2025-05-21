import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ConfigurationError
from bson.objectid import ObjectId # Importante para convertir el _id string a ObjectId

# --- Configuración de MongoDB Atlas ---
MONGO_URI = "mongodb+srv://axmadlar:pw1234@cluster0.rrnubrd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "proyecto"
COLLECTION_NAME = "usuarios"

class MongoDBCollectionViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"Modulo de Gestión de Usuarios")
        self.geometry("1000x650")

        self.mongo_uri = MONGO_URI
        self.client = None

        # --- Frame para Controles ---
        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill=tk.X)

        self.refresh_button = ttk.Button(control_frame, text="Actualizar Registros", command=self.load_records)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        self.toggle_button = ttk.Button(control_frame, text="Alternar Estado Préstamo", command=self.toggle_prestamo_status)
        self.toggle_button.pack(side=tk.LEFT, padx=(0,10))

        self.status_label = ttk.Label(control_frame, text="Iniciando...") # Cambiado el texto inicial
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # --- Frame para la Tabla (Treeview) ---
        table_frame = ttk.Frame(self, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("nombre", "apellidos", "email", "prestamos")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("apellidos", text="Apellidos")
        self.tree.heading("email", text="Email")
        self.tree.heading("prestamos", text="Préstamos Autorizados")

        self.tree.column("nombre", width=150, minwidth=100, stretch=tk.YES)
        self.tree.column("apellidos", width=200, minwidth=150, stretch=tk.YES)
        self.tree.column("email", width=250, minwidth=200, stretch=tk.YES)
        self.tree.column("prestamos", width=150, minwidth=120, anchor=tk.CENTER, stretch=tk.YES)

        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Cargar registros automáticamente al inicio ---
        self.load_records() # <--- ESTA LÍNEA SE ACTIVA/AÑADE

    def get_mongo_client(self):
        try:
            # Revalida la conexión si ya existe un cliente o si self.client es None
            if not self.client or not self.client.admin.command('ping'):
                if self.client:
                    try: self.client.close()
                    except: pass
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=10000)
                self.client.admin.command('ping') # Verifica la nueva conexión
            return self.client
        except ConfigurationError as e:
            self.status_label.config(text=f"Error de Configuración URI: {str(e)}", foreground="red")
            messagebox.showerror("Error de Configuración", f"La URI de conexión no es válida: {str(e)}")
            self.client = None
            return None
        except (ConnectionFailure, OperationFailure) as e:
            self.status_label.config(text=f"Error de Conexión/Operación: {str(e)}", foreground="red")
            messagebox.showerror("Error de Conexión", f"No se pudo conectar o validar la conexión a MongoDB Atlas.\nDetalle: {str(e)}")
            self.client = None
            return None

    def load_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.status_label.config(text=f"Cargando registros...", foreground="blue")
        self.update_idletasks() # Asegura que el mensaje "Cargando..." se muestre

        client = self.get_mongo_client()
        if not client:
            self.status_label.config(text="Fallo al conectar. Verifica la consola o reintenta.", foreground="red")
            return

        try:
            db = client[DATABASE_NAME]
            collection = db[COLLECTION_NAME]
            records = list(collection.find({}))

            if records:
                for record in records:
                    record_id_str = str(record.get('_id'))
                    nombre = record.get('nombre', 'N/D')
                    apellidos = record.get('apellidos', 'N/D')
                    email = record.get('email', 'N/D')

                    autorizado_raw = record.get('autorizado_para_prestamos')
                    estado_prestamo = "Autorizado" if autorizado_raw is True else "Denegado"

                    self.tree.insert("", tk.END, iid=record_id_str, values=(nombre, apellidos, email, estado_prestamo))
                self.status_label.config(text=f"Se encontraron {len(records)} registros.", foreground="green")
            else:
                self.status_label.config(text=f"No se encontraron registros en '{COLLECTION_NAME}'.", foreground="orange")

        except OperationFailure as e:
            error_msg = e.details.get('errmsg', str(e))
            self.status_label.config(text=f"Error al cargar: {error_msg}", foreground="red")
            messagebox.showerror("Error de MongoDB", f"No se pudieron obtener los registros: {error_msg}")
        except Exception as e:
            self.status_label.config(text=f"Error inesperado al cargar: {str(e)}", foreground="red")
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {str(e)}")

    def toggle_prestamo_status(self):
        selected_item_iid = self.tree.focus()

        if not selected_item_iid:
            messagebox.showwarning("Selección Requerida", "Por favor, selecciona un usuario de la tabla para cambiar su estado de préstamo.")
            return

        try:
            current_values = self.tree.item(selected_item_iid, 'values')
            current_prestamo_display_status = current_values[3]

            new_boolean_status = (current_prestamo_display_status == "Denegado")
            mongo_doc_id = ObjectId(selected_item_iid)

            client = self.get_mongo_client()
            if not client:
                messagebox.showerror("Error de Conexión", "No se pudo conectar a MongoDB para actualizar.")
                return

            db = client[DATABASE_NAME]
            collection = db[COLLECTION_NAME]

            update_result = collection.update_one(
                {'_id': mongo_doc_id},
                {'$set': {'autorizado_para_prestamos': new_boolean_status}}
            )

            if update_result.modified_count > 0:
                messagebox.showinfo("Éxito", f"El estado de préstamo ha sido cambiado a {'Autorizado' if new_boolean_status else 'Denegado'}.")
                self.load_records()
            elif update_result.matched_count == 1 and update_result.modified_count == 0:
                 messagebox.showinfo("Información", "El estado del préstamo ya era el solicitado. No se realizaron cambios.")
            else:
                messagebox.showerror("Error de Actualización", "No se pudo encontrar o actualizar el usuario.")

        except OperationFailure as e:
            error_msg = e.details.get('errmsg', str(e))
            self.status_label.config(text=f"Error al actualizar: {error_msg}", foreground="red")
            messagebox.showerror("Error de MongoDB", f"No se pudo actualizar el estado: {error_msg}")
        except IndexError:
            messagebox.showerror("Error Interno", "No se pudieron obtener los datos del usuario seleccionado.")
        except Exception as e:
            self.status_label.config(text=f"Error inesperado al actualizar: {str(e)}", foreground="red")
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al cambiar el estado: {str(e)}")

    def on_closing(self):
        if self.client:
            try:
                self.client.close()
                print("Conexión a MongoDB cerrada.")
            except Exception as e:
                print(f"Error al cerrar la conexión de MongoDB: {e}")
        self.destroy()

if __name__ == "__main__":
    app = MongoDBCollectionViewer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()