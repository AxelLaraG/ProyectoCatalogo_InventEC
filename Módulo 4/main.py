import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import DateEntry
from datetime import datetime
from conexion import conectar_mongo


class PrestamoDAO:
    def __init__(self, db):
        self.collection = db['prestamos']

    def registrar_prestamo(self, equipo_id, usuario_id, fecha_prestamo, fecha_devolucion_prevista, comentarios):
        prestamo = {
            "equipo_id": equipo_id,
            "usuario_id": usuario_id,
            "fecha_prestamo": fecha_prestamo,
            "fecha_devolucion_prevista": fecha_devolucion_prevista,
            "fecha_devolucion_real": None,
            "comentarios": comentarios
        }
        result = self.collection.insert_one(prestamo)
        return result.inserted_id

    def registrar_devolucion(self, prestamo_id, fecha_devolucion_real):
        self.collection.update_one(
            {"_id": prestamo_id},
            {"$set": {"fecha_devolucion_real": fecha_devolucion_real}}
        )
    def listar_prestamo(self):
        return list(self.collection.find())

class EquipoDAO:
    def __init__(self, db):
        self.collection = db['equipos']

    def actualizar_estado(self, equipo_id, nuevo_estado):
        self.collection.update_one(
            {"_id": equipo_id},
            {"$set": {"estado": nuevo_estado}}
        )

    def listar_equipos(self):
        return list(self.collection.find())

class UsuarioDAO:
    def __init__(self, db):
        self.collection = db['usuarios']

    def listar_usuarios(self):
        return list(self.collection.find())

class AppPrestamos:
    def __init__(self, root):
        self.db = conectar_mongo()
        self.prestamo_dao = PrestamoDAO(self.db)
        self.equipo_dao = EquipoDAO(self.db)
        self.usuario_dao = UsuarioDAO(self.db)

        root.title("Gestión de Préstamos de Equipos")
        root.geometry("700x200")

        self.create_widgets()
        self.load_equipos()
        self.load_usuarios()

    def create_widgets(self):
        frame = ttk.Frame()
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Equipo:").grid(row=0, column=0, sticky=tk.W)
        self.combo_equipo = ttk.Combobox(frame, state="readonly", width=50)
        self.combo_equipo.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(frame, text="Usuario:").grid(row=1, column=0, sticky=tk.W)
        self.combo_usuario = ttk.Combobox(frame, state="readonly", width=50)
        self.combo_usuario.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(frame, text="Fecha Préstamo:").grid(row=2, column=0, sticky=tk.W)
        self.date_prestamo = DateEntry(frame, date_pattern="yyyy-MM-dd")
        self.date_prestamo.grid(row=2, column=1, sticky=tk.W, padx=(0,5))
        self.hour_prestamo = ttk.Spinbox(frame, from_=0, to=23, width=3, format="%02.0f")
        self.hour_prestamo.set("10")
        self.hour_prestamo.grid(row=2, column=1, sticky=tk.W, padx=(130,5))
        ttk.Label(frame, text=":").grid(row=2, column=1, sticky=tk.W, padx=(180,5))
        self.minute_prestamo = ttk.Spinbox(frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_prestamo.set("00")
        self.minute_prestamo.grid(row=2, column=1, sticky=tk.W, padx=(185,5))

        ttk.Label(frame, text="Fecha Devolución Prevista:").grid(row=3, column=0, sticky=tk.W)
        self.date_devol_prev = DateEntry(frame, date_pattern="yyyy-MM-dd")
        self.date_devol_prev.grid(row=3, column=1, sticky=tk.W, padx=(0,5))
        self.hour_devol_prev = ttk.Spinbox(frame, from_=0, to=23, width=3, format="%02.0f")
        self.hour_devol_prev.set("10")
        self.hour_devol_prev.grid(row=3, column=1, sticky=tk.W, padx=(130,5))
        ttk.Label(frame, text=":").grid(row=3, column=1, sticky=tk.W, padx=(180,5))
        self.minute_devol_prev = ttk.Spinbox(frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_devol_prev.set("00")
        self.minute_devol_prev.grid(row=3, column=1, sticky=tk.W, padx=(185,5))

        ttk.Label(frame, text="Comentarios:").grid(row=4, column=0, sticky=tk.W)
        self.entry_comentarios = ttk.Entry(frame, width=50)
        self.entry_comentarios.grid(row=4, column=1, columnspan=2, sticky=tk.W)

        ttk.Button(frame, text="Registrar Préstamo", command=self.registrar_prestamo).grid(row=5, column=0, pady=10)
        ttk.Button(frame, text="Registrar Devolución", command=self.registrar_devolucion).grid(row=5, column=1, pady=10)

    def load_equipos(self):
        equipos = self.equipo_dao.listar_equipos()
        disponibles = [eq for eq in equipos if eq['estado'] == 'Disponible']
        self.equipos_map = {str(eq['_id']): eq for eq in disponibles}
        self.combo_equipo['values'] = [f"{eq['nombre']} (ID: {eq['_id']})" for eq in disponibles]

    def load_usuarios(self):
        usuarios = self.usuario_dao.listar_usuarios()
        disponibles = [u for u in usuarios if u['autorizado_para_prestamos'] == True]
        self.usuarios_map = {str(u['_id']): u for u in disponibles}
        self.combo_usuario['values'] = [f"{u['nombre']} {u['apellidos']} (ID: {u['_id']})" for u in disponibles]

    def registrar_prestamo(self):
        try:
            equipo_str = self.combo_equipo.get()
            equipo_id = next(key for key in self.equipos_map if f"ID: {key}" in equipo_str)
            usuario_str = self.combo_usuario.get()
            usuario_id = next(key for key in self.usuarios_map if f"ID: {key}" in usuario_str)

            fecha_p_str = (
                f"{self.date_prestamo.get()} "
                f"{int(self.hour_prestamo.get()):02d}:"
                f"{int(self.minute_prestamo.get()):02d}"
            )
            fecha_p = datetime.strptime(fecha_p_str, "%Y-%m-%d %H:%M")

            fecha_d_str = (
                f"{self.date_devol_prev.get()} "
                f"{int(self.hour_devol_prev.get()):02d}:"
                f"{int(self.minute_devol_prev.get()):02d}"
            )
            fecha_dev_prev = datetime.strptime(fecha_d_str, "%Y-%m-%d %H:%M")
            comentarios = self.entry_comentarios.get()

            prestamo_id = self.prestamo_dao.registrar_prestamo(equipo_id, usuario_id, fecha_p, fecha_dev_prev, comentarios)
            self.equipo_dao.actualizar_estado(equipo_id, 'Prestado')

            messagebox.showinfo("Éxito", f"Préstamo registrado (ID: {prestamo_id})")
            self.load_equipos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def registrar_devolucion(self):
        pendientes = list(self.db['prestamos'].find({"fecha_devolucion_real": None}))
        if not pendientes:
            messagebox.showinfo("Info", "No hay préstamos pendientes.")
            return

        dlg = tk.Toplevel()
        dlg.title("Seleccionar préstamo a devolver")
        dlg.geometry("800x300")

        lb = tk.Listbox(dlg, width=90, height=10)
        scrollbar = ttk.Scrollbar(dlg, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=scrollbar.set)

        self._pendientes_map = {}
        for idx, prest in enumerate(pendientes):
            try:
                equipo = self.db['equipos'].find_one({"_id": ObjectId(prest['equipo_id'])})
            except Exception:
                equipo = None
            try:
                usuario = self.db['usuarios'].find_one({"_id": ObjectId(prest['usuario_id'])})
            except Exception:
                usuario = None
            nombre_equipo = equipo['nombre'] if equipo else str(prest['equipo_id'])
            nombre_usuario = usuario['nombre'] if usuario else str(prest['usuario_id'])

            texto = (f"ID:{prest['_id']} — Equipo:{nombre_equipo} "
                    f"Usuario:{nombre_usuario} Préstamo:{prest['fecha_prestamo'].strftime('%Y-%m-%d %H:%M')}")
            lb.insert(tk.END, texto)
            self._pendientes_map[idx] = prest

        lb.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Cancelar", command=dlg.destroy).pack(side=tk.LEFT, padx=5)
        def confirmar():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Atención", "Selecciona un préstamo.")
                return
            prest = self._pendientes_map[sel[0]]
            fecha_real = datetime.now()
            self.prestamo_dao.registrar_devolucion(prest['_id'], fecha_real)
            self.equipo_dao.actualizar_estado(prest['equipo_id'], 'Disponible')
            messagebox.showinfo("Éxito", f"Devolución registrada a las {fecha_real.strftime('%Y-%m-%d %H:%M')}")
            dlg.destroy()
            self.load_equipos()

        ttk.Button(btn_frame, text="Confirmar devolución", command=confirmar).pack(side=tk.LEFT, padx=5)

        dlg.transient(self.root)
        dlg.grab_set()
        self.root.wait_window(dlg)

if __name__ == '__main__':
    root = tk.Tk()
    app = AppPrestamos(root)
    root.mainloop()