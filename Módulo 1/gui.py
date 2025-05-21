import tkinter as tk
from tkinter import ttk
from conexion import conectar_mongo
from operaciones import obtener_todos_los_equipos, buscar_por_campo
from utils import formatear_valor

class CatalogoGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Catálogo de Equipamiento")
        self.master.geometry("1000x550")
        self.master.configure(bg="#F5F7FA")
        self.db = conectar_mongo()
        self.coleccion = self.db["equipos"]

        self.mapeo_campos = {
            "_id": "ID",
            "nombre": "Nombre",
            "modelo": "Modelo",
            "numero_serie": "Número de serie",
            "estado": "Estado",
            "ubicacion": "Ubicación"
        }

        self.opciones_busqueda = {
            "Nombre": "nombre",
            "Modelo": "modelo",
            "Número de serie": "numero_serie",
            "Ubicación": "ubicacion",
            "Todos": "todos"
        }

        self.crear_widgets()
        self.cargar_equipos()

    def crear_widgets(self):
        titulo = tk.Label(self.master, text="Catálogo de Equipamiento Audiovisual",
                          font=("Segoe UI", 18, "bold"), bg="#F5F7FA", fg="#2C3E50")
        titulo.pack(pady=10)

        marco_busqueda = tk.Frame(self.master, bg="#F5F7FA")
        marco_busqueda.pack(pady=5)

        tk.Label(marco_busqueda, text="Buscar:", bg="#F5F7FA", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
        self.entry_busqueda = tk.Entry(marco_busqueda, width=30)
        self.entry_busqueda.grid(row=0, column=1, padx=5)

        tk.Label(marco_busqueda, text="en", bg="#F5F7FA", font=("Segoe UI", 11)).grid(row=0, column=2)
        self.campo_busqueda = ttk.Combobox(marco_busqueda, values=list(self.opciones_busqueda.keys()), state="readonly")
        self.campo_busqueda.set("Todos")
        self.campo_busqueda.grid(row=0, column=3, padx=5)

        btn_buscar = tk.Button(marco_busqueda, text="Buscar", command=self.buscar_equipo,
                               bg="#3498DB", fg="white", font=("Segoe UI", 10), relief="flat")
        btn_buscar.grid(row=0, column=4, padx=5)
        btn_todos = tk.Button(marco_busqueda, text="Mostrar Todos", command=self.cargar_equipos,
                              bg="#1ABC9C", fg="white", font=("Segoe UI", 10), relief="flat")
        btn_todos.grid(row=0, column=5, padx=5)

        tk.Label(marco_busqueda, text="Filtrar por Estado:", bg="#F5F7FA", font=("Segoe UI", 11)).grid(row=1, column=0, pady=10)
        self.combo_estado = ttk.Combobox(marco_busqueda, values=["Todos", "Disponible", "Prestado", "En mantenimiento"], state="readonly")
        self.combo_estado.set("Todos")
        self.combo_estado.grid(row=1, column=1, padx=5)
        self.combo_estado.bind("<<ComboboxSelected>>", self.filtrar_estado)

        self.columnas = ("_id", "nombre", "modelo", "numero_serie", "estado", "ubicacion")
        self.tree = ttk.Treeview(self.master, columns=self.columnas, show="headings", height=15)
        self.tree.pack(pady=10, fill="both", expand=True)

        for col in self.columnas:
            encabezado = self.mapeo_campos.get(col, col)
            self.tree.heading(col, text=encabezado)
            self.tree.column(col, anchor="center", width=150)

        estilo = ttk.Style()
        estilo.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

    def cargar_equipos(self):
        self.limpiar_tabla()
        equipos = obtener_todos_los_equipos(self.coleccion)
        self.insertar_en_tabla(equipos)

    def buscar_equipo(self):
        valor = self.entry_busqueda.get().strip().lower()
        campo_mostrado = self.campo_busqueda.get().strip()
        campo = self.opciones_busqueda.get(campo_mostrado, "todos")
        self.limpiar_tabla()
        equipos = buscar_por_campo(self.coleccion, campo, valor)
        self.insertar_en_tabla(equipos)

    def filtrar_estado(self, event):
        estado = self.combo_estado.get().strip().lower()
        self.limpiar_tabla()
        if estado == "todos":
            equipos = obtener_todos_los_equipos(self.coleccion)
        else:
            equipos = buscar_por_campo(self.coleccion, "estado", estado)
        self.insertar_en_tabla(equipos)

    def limpiar_tabla(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def insertar_en_tabla(self, equipos):
        for equipo in equipos:
            self.tree.insert("", tk.END, values=(
                str(equipo.get("_id", "")),
                formatear_valor(equipo.get("nombre")),
                formatear_valor(equipo.get("modelo")),
                formatear_valor(equipo.get("numero_serie")),
                formatear_valor(equipo.get("estado")),
                formatear_valor(equipo.get("ubicacion"))
            ))