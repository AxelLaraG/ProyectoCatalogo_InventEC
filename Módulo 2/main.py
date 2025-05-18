import tkinter as tk
from tkinter import ttk, messagebox, font
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import urllib.parse
from datetime import datetime

class MiVentana:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Equipamiento")
        self.root.geometry("1150x700")
        self.base_font = ('Calibri', 11)
        self.title_font = ('Calibri', 14, 'bold')  
        
        self.conexion_mongo()
        
        self.estilos_ventana()

        self.crear_widgets()
        self.cargar_info()
    
    def conexion_mongo(self):
        try:
            usr = "axmadlar"
            pswd = "pw1234"
            url = "cluster0.rrnubrd.mongodb.net"
            nom_base = "proyecto"

            pswd_correcta = urllib.parse.quote_plus(pswd)
            
            cadena_conn = (
                f"mongodb+srv://{usr}:{pswd_correcta}@{url}/"
                f"{nom_base}?retryWrites=true&w=majority"
            )
            
            self.client = MongoClient(
                cadena_conn,
                server_api=ServerApi('1'),
                tls=True,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000
            )
            
            self.client.admin.command('ping')
            print("Conexión exitosa a Mongo")
            
            self.db = self.client[nom_base]
            self.collection = self.db['equipos']
        
            if 'equipos' not in self.db.list_collection_names():
                self.db.create_collection('equipos')
                print("Colección 'equipos' creada")
            
        except Exception as e:
            messagebox.showerror(
                "Error de Conexión", 
                f"No se pudo hacer la conexión a Mongo:\n{str(e)}\n\n"
            )
            self.root.destroy()
    
    def estilos_ventana(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.fondo_color = '#FAF6E9'  
        self.entradas_color = '#FFFDF6'#color de fondo de las entradas
        self.btn_color = '#5F8B4C'#color de los botones
        self.text_color = '#945034'#color del título
        #color de objetos al ser seleccionados=#753742
        
        self.style.configure('.', 
                           font=self.base_font,
                           background=self.fondo_color)

        self.style.configure('Main.TFrame',
                           background=self.fondo_color)
        
        self.style.configure('Form.TLabelframe',
                           background=self.fondo_color,
                           bordercolor=self.text_color)
        
        self.style.configure('Form.TLabelframe.Label',
                           font=self.title_font,
                           foreground=self.text_color,
                           background=self.fondo_color)

        self.style.configure('TEntry',
                           fieldbackground=self.entradas_color,
                           foreground='#333333',
                           bordercolor='#753742',
                           padding=10)

        self.style.configure('TCombobox',
                           fieldbackground=self.entradas_color,
                           foreground='#333333',
                           bordercolor=self.text_color,
                           padding=5,
                           selectbackground=self.btn_color)

        self.style.configure('TButton',
                           foreground='white',
                           background=self.btn_color,
                           padding=8,
                           width=18)
        
        self.style.map('TButton',
                     background=[('active', '#753742')])

        self.style.configure('Treeview',
                           background=self.entradas_color,
                           foreground='#333333',
                           fieldbackground=self.entradas_color,
                           rowheight=28,
                           padding=0)
        
        self.style.configure('Treeview.Heading',
                           font=self.base_font,
                           foreground='white',
                           background=self.text_color,
                           padding=0)
        
        self.style.map('Treeview',
                     background=[('selected', '#753742')],
                     foreground=[('selected', 'white')])
    
    def crear_widgets(self):
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        form_frame = ttk.LabelFrame(main_frame, 
                                  text="Información del equipo",
                                  style='Form.TLabelframe',
                                  padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        self.crear_formulario(form_frame)

        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Guardar", command=self.guardar).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Editar equipo", command=self.editar).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Eliminar equipo", command=self.eliminar).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Limpiar entradas", command=self.limpiar_formulario).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Actualizar lista", command=self.cargar_info).pack(side=tk.LEFT, padx=5)

        self.crear_tabla(main_frame)
    
    def crear_formulario(self, parent):
        parent.columnconfigure(1, weight=1, pad=10)

        ttk.Label(parent, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nombre_entrada = ttk.Entry(parent, style='TEntry', font=('Calibri', 11))
        self.nombre_entrada.grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(parent, text="Modelo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.modelo_entrada = ttk.Entry(parent, style='TEntry',font=('Calibri', 11))
        self.modelo_entrada.grid(row=1, column=1, sticky=tk.EW, pady=5)
  
        ttk.Label(parent, text="Número de Serie:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.numserie_entrada = ttk.Entry(parent, style='TEntry',font=('Calibri', 11))
        self.numserie_entrada.grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(parent, text="Estado del equipo:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.estado_combobox = ttk.Combobox(parent, 
                                          values=["Disponible", "Prestado","En mantenimiento"],
                                          style='TCombobox',font=('Calibri', 11))
        self.estado_combobox.grid(row=3, column=1, sticky=tk.EW, pady=5)
        self.estado_combobox.current(0)
        
        ttk.Label(parent, text="Ubicación:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ubicacion_entrada = ttk.Entry(parent, style='TEntry',font=('Calibri', 11))
        self.ubicacion_entrada.grid(row=4, column=1, sticky=tk.EW, pady=5)
    
    def crear_tabla(self, parent):
        tree_frame = ttk.Frame(parent, style='Main.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, 
                               columns=("nombre", "modelo", "serie", "estado", "ubicacion","fecha"), 
                               show="headings", 
                               height=15,
                               style='Treeview')
        
        self.tree.heading("nombre", text="Nombre", anchor=tk.CENTER)
        self.tree.heading("modelo", text="Modelo", anchor=tk.CENTER)
        self.tree.heading("serie", text="Número de Serie", anchor=tk.CENTER)
        self.tree.heading("estado", text="Estado", anchor=tk.CENTER)
        self.tree.heading("ubicacion", text="Ubicación", anchor=tk.CENTER)
        self.tree.heading("fecha", text="Fecha de registro", anchor=tk.CENTER)
        
        self.tree.column("nombre", width=220, anchor=tk.CENTER)
        self.tree.column("modelo", width=100, anchor=tk.CENTER)
        self.tree.column("serie", width=150, anchor=tk.CENTER)
        self.tree.column("estado", width=150, anchor=tk.CENTER)
        self.tree.column("ubicacion", width=110, anchor=tk.CENTER)
        self.tree.column("fecha", width=100, anchor=tk.CENTER)

        v_scrollb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollb.set, xscrollcommand=h_scrollb.set)
        
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        v_scrollb.grid(row=0, column=1, sticky=tk.NS)
        h_scrollb.grid(row=1, column=0, sticky=tk.EW)
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_equipo)
        
        self.selected_id = None
        
    def cargar_info(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
        equipos = list(self.collection.find().sort("nombre", 1))
    
        for equipo in equipos:
            try:
                fecha = equipo.get('fecha_registro', datetime.now())
                if isinstance(fecha, datetime):
                    fecha_str = fecha.strftime("%d/%m/%Y %H:%M")
                else:
                    fecha_str = "N/A"
        
                self.tree.insert("", tk.END,
                       values=(equipo['nombre'],
                              equipo['modelo'],
                              equipo['numero_serie'], 
                              equipo['estado'],
                              equipo['ubicacion'],
                              fecha_str),
                       iid=str(equipo['_id']))
            except Exception as e:
                print(f"Error cargando equipo {equipo.get('_id')}: {str(e)}")
                
    def seleccionar_equipo(self, event):
        item_seleccionado = self.tree.focus()
        if not item_seleccionado:
            return
            
        self.selected_id = item_seleccionado
        item_data = self.tree.item(item_seleccionado)['values']
        
        self.nombre_entrada.delete(0, tk.END)
        self.nombre_entrada.insert(0, item_data[0])
        
        self.modelo_entrada.delete(0, tk.END)
        self.modelo_entrada.insert(0, item_data[1])
        
        self.numserie_entrada.delete(0, tk.END)
        self.numserie_entrada.insert(0, item_data[2])
        
        self.estado_combobox.set(item_data[3])
        
        self.ubicacion_entrada.delete(0, tk.END)
        self.ubicacion_entrada.insert(0, item_data[4])
    
    def guardar(self):
        nombre = self.nombre_entrada.get().strip()
        modelo = self.modelo_entrada.get().strip()
        serie = self.numserie_entrada.get().strip()
        ubi = self.ubicacion_entrada.get().strip()
        edo = self.estado_combobox.get()

        if not all([nombre, modelo, serie, ubi, edo]):
            messagebox.showerror("Error", "No ha llenado todos los campos", parent=self.root)
            return

        equipo_info = {
        "nombre": nombre,
        "modelo": modelo,
        "numero_serie": serie,
        "estado": edo,
        "ubicacion": ubi,
        "fecha_registro": datetime.now()
        }

        try:
            if self.selected_id:  
                equipo_actual = self.collection.find_one({"_id": ObjectId(self.selected_id)})
                if nombre != equipo_actual['nombre']:
                    if self.collection.find_one({"nombre": nombre, "_id": {"$ne": ObjectId(self.selected_id)}}):
                        messagebox.showerror("Error", "Ya existe hay un equipo registrado con ese nombre", parent=self.root)
                        return

                result = self.collection.update_one(
                    {"_id": ObjectId(self.selected_id)},
                    {"$set": equipo_info}
                )
                if result.modified_count > 0:
                    messagebox.showinfo("Éxito", "Equipo editado exitosamente", parent=self.root)
                else:
                    messagebox.showinfo("Información", "No se hicieron cambios", parent=self.root)

            else:
                if self.collection.find_one({"nombre": nombre}):
                    messagebox.showerror("Error", "Ya existe un equipo con este nombre", parent=self.root)
                    return

                result = self.collection.insert_one(equipo_info)
                self.selected_id = str(result.inserted_id)
                messagebox.showinfo("Éxito", "Equipo guardado exitosamente", parent=self.root)

            self.cargar_info()
            self.selected_id = None
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}", parent=self.root)

    def editar(self):
        if not self.selected_id:
            messagebox.showwarning("Selección requerida", "Seleccione el equipo que desea editar", parent=self.root)
            return
        self.nombre_entrada.focus_set()
    
    def eliminar(self):
        if not self.selected_id:
            messagebox.showwarning("Selección requerida", "Seleccione el equipo que desea eliminar", parent=self.root)
            return
            
        if messagebox.askyesno(
            "Confirmación",
            f"¿Está seguro que desea eliminar este equipo?\n\n"
            f"Nombre: {self.nombre_entrada.get()}\n"
            f"Modelo: {self.modelo_entrada.get()}\n",
            parent=self.root
        ):
            try:
                result = self.collection.delete_one({"_id": ObjectId(self.selected_id)})
                if result.deleted_count > 0:
                    messagebox.showinfo("Éxito", "El equipo ha sido eliminado con éxito", parent=self.root)
                    self.limpiar_formulario()
                    self.cargar_info()
                else:
                    messagebox.showwarning("Advertencia", "No se encontró el equipo a eliminar", parent=self.root)
            
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el equipo que usted selecciono", parent=self.root)
    
    def limpiar_formulario(self):
        self.selected_id = None
        self.nombre_entrada.delete(0, tk.END)
        self.modelo_entrada.delete(0, tk.END)
        self.numserie_entrada.delete(0, tk.END)
        self.estado_combobox.current(0)
        self.ubicacion_entrada.delete(0, tk.END)

        for item in self.tree.selection():
            self.tree.selection_remove(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = MiVentana(root)
    root.mainloop()
