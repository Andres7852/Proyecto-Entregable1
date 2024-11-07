import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from proyecto.app import (
    EstudioPersonalizado, 
    leer_docx, 
    leer_pdf, 
    EstudioError, 
    DocumentoVacioError,
    ProcesamientoError
)
import os
from datetime import datetime
from typing import Optional

class InterfazEstudio:
    def __init__(self):
        self.estudio = EstudioPersonalizado()
        self.archivo_actual: Optional[str] = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz gráfica principal"""
        self.root = tk.Tk()
        self.root.title("Sistema de Estudio Personalizado")
        self.root.geometry("1000x800")
        
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Action.TButton", padding=5)
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        doc_label = ttk.Label(left_frame, text="Contenido del Documento", style="Header.TLabel")
        doc_label.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        self.text_area = scrolledtext.ScrolledText(
            left_frame, 
            width=50, 
            height=30,
            wrap=tk.WORD,
            font=("Helvetica", 10)
        )
        self.text_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.rowconfigure(1, weight=1)
        left_frame.columnconfigure(0, weight=1)
        
        actions_frame = ttk.Frame(left_frame)
        actions_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(
            actions_frame,
            text="Cargar Documento",
            command=self.cargar_archivo,
            style="Action.TButton"
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            actions_frame,
            text="Limpiar",
            command=self.limpiar_contenido,
            style="Action.TButton"
        ).grid(row=0, column=1, padx=5)
        
        result_label = ttk.Label(right_frame, text="Resultados", style="Header.TLabel")
        result_label.grid(row=0, column=0, pady=5, sticky=tk.W)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        self.setup_tabs()
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_var.set("Listo")
        
    def setup_tabs(self):
        """Configura las pestañas del notebook"""
        resumen_frame = ttk.Frame(self.notebook)
        self.notebook.add(resumen_frame, text="Resumen")
        ttk.Button(
            resumen_frame,
            text="Generar Resumen",
            command=self.mostrar_resumen,
            style="Action.TButton"
        ).grid(row=0, column=0, pady=5)
        self.resumen_area = self.crear_area_texto(resumen_frame, 1)
        
        conceptos_frame = ttk.Frame(self.notebook)
        self.notebook.add(conceptos_frame, text="Conceptos Clave")
        ttk.Button(
            conceptos_frame,
            text="Extraer Conceptos",
            command=self.mostrar_conceptos_clave,
            style="Action.TButton"
        ).grid(row=0, column=0, pady=5)
        self.conceptos_area = self.crear_area_texto(conceptos_frame, 1)
        
        preguntas_frame = ttk.Frame(self.notebook)
        self.notebook.add(preguntas_frame, text="Preguntas")
        ttk.Button(
            preguntas_frame,
            text="Generar Preguntas",
            command=self.mostrar_preguntas,
            style="Action.TButton"
        ).grid(row=0, column=0, pady=5)
        self.preguntas_area = self.crear_area_texto(preguntas_frame, 1)
        
        fichas_frame = ttk.Frame(self.notebook)
        self.notebook.add(fichas_frame, text="Fichas")
        
        tipos_frame = ttk.Frame(fichas_frame)
        tipos_frame.grid(row=0, column=0, pady=5)
        
        self.tipo_ficha = tk.StringVar(value="hemerografica")
        for i, tipo in enumerate([
            ("Hemerográfica", "hemerografica"),
            ("Electrónica", "electronica"),
            ("Bibliográfica", "bibliografica"),
            ("Catalográfica", "catalografica"),
            ("Textual", "textual"),
            ("Resumen", "resumen")
        ]):
            ttk.Radiobutton(
                tipos_frame,
                text=tipo[0],
                value=tipo[1],
                variable=self.tipo_ficha
            ).grid(row=0, column=i, padx=5)
            
        ttk.Button(
            fichas_frame,
            text="Generar Ficha",
            command=self.mostrar_ficha,
            style="Action.TButton"
        ).grid(row=1, column=0, pady=5)
        
        self.fichas_area = self.crear_area_texto(fichas_frame, 2)
        
    def crear_area_texto(self, parent, row):
        """Crea un área de texto scrolleable"""
        area = scrolledtext.ScrolledText(
            parent,
            width=50,
            height=25,
            wrap=tk.WORD,
            font=("Helvetica", 10)
        )
        area.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(0, weight=1)
        return area
        
    def cargar_archivo(self):
        """Maneja la carga de archivos"""
        try:
            archivo = filedialog.askopenfilename(
                filetypes=[("Documentos", "*.pdf;*.docx")]
            )
            if not archivo:
                return
                
            self.archivo_actual = archivo
            extension = os.path.splitext(archivo)[1].lower()
            
            self.status_var.set(f"Cargando archivo: {os.path.basename(archivo)}...")
            self.root.update()
            
            if extension == '.pdf':
                texto = leer_pdf(archivo)
            elif extension == '.docx':
                texto = leer_docx(archivo)
            else:
                raise ValueError("Formato de archivo no soportado")
                
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, texto)
            self.status_var.set(f"Archivo cargado: {os.path.basename(archivo)}")
            
        except DocumentoVacioError as e:
            messagebox.showerror("Error", f"El documento está vacío: {str(e)}")
            self.status_var.set("Error: Documento vacío")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")
            self.status_var.set("Error al cargar el archivo")
            
    def limpiar_contenido(self):
        """Limpia todas las áreas de texto"""
        self.text_area.delete(1.0, tk.END)
        self.resumen_area.delete(1.0, tk.END)
        self.conceptos_area.delete(1.0, tk.END)
        self.preguntas_area.delete(1.0, tk.END)
        self.fichas_area.delete(1.0, tk.END)
        self.archivo_actual = None
        self.status_var.set("Contenido limpiado")
        
    def obtener_texto(self):
        """Obtiene el texto del área principal"""
        texto = self.text_area.get(1.0, tk.END).strip()
        if not texto:
            raise DocumentoVacioError("No hay texto para procesar")
        return texto
        
    def mostrar_resumen(self):
        """Genera y muestra el resumen del texto"""
        try:
            texto = self.obtener_texto()
            self.status_var.set("Generando resumen...")
            self.root.update()
            
            resumen = self.estudio.generar_resumen(texto)
            self.resumen_area.delete(1.0, tk.END)
            self.resumen_area.insert(tk.END, resumen)
            
            self.status_var.set("Resumen generado exitosamente")
            self.notebook.select(0) 
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar resumen: {str(e)}")
            self.status_var.set("Error al generar resumen")
            
    def mostrar_conceptos_clave(self):
        """Extrae y muestra los conceptos clave"""
        try:
            texto = self.obtener_texto()
            self.status_var.set("Extrayendo conceptos clave...")
            self.root.update()
            
            conceptos = self.estudio.extraer_conceptos_clave(texto)
            self.conceptos_area.delete(1.0, tk.END)
            for i, concepto in enumerate(conceptos, 1):
                self.conceptos_area.insert(tk.END, f"{i}. {concepto}\n")
                
            self.status_var.set("Conceptos clave extraídos exitosamente")
            self.notebook.select(1) 
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al extraer conceptos: {str(e)}")
            self.status_var.set("Error al extraer conceptos")
            
    def mostrar_preguntas(self):
        """Genera y muestra preguntas de estudio"""
        try:
            texto = self.obtener_texto()
            self.status_var.set("Generando preguntas...")
            self.root.update()
            
            preguntas = self.estudio.generar_preguntas(texto)
            self.preguntas_area.delete(1.0, tk.END)
            for i, pregunta in enumerate(preguntas, 1):
                self.preguntas_area.insert(tk.END, f"{i}. {pregunta}\n\n")
                
            self.status_var.set("Preguntas generadas exitosamente")
            self.notebook.select(2) 
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar preguntas: {str(e)}")
            self.status_var.set("Error al generar preguntas")
            
    def mostrar_ficha(self):
        """Genera y muestra la ficha seleccionada"""
        try:
            texto = self.obtener_texto()
            tipo = self.tipo_ficha.get()
            self.status_var.set(f"Generando ficha {tipo}...")
            self.root.update()
            
            metodos_ficha = {
                "hemerografica": self.estudio.crear_ficha_hemerografica,
                "electronica": self.estudio.crear_ficha_electronica,
                "bibliografica": self.estudio.crear_ficha_bibliografica,
                "catalografica": self.estudio.crear_ficha_catalografica,
                "textual": self.estudio.crear_ficha_textual,
                "resumen": self.estudio.crear_ficha_resumen
            }
            
            ficha = metodos_ficha[tipo](texto)
            self.fichas_area.delete(1.0, tk.END)
            self.fichas_area.insert(tk.END, str(ficha))
            
            self.status_var.set(f"Ficha {tipo} generada exitosamente")
            self.notebook.select(3)  
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar ficha: {str(e)}")
            self.status_var.set("Error al generar ficha")
            
    def ejecutar(self):
        """Inicia la aplicación"""
        self.root.mainloop()

def main():
    interfaz = InterfazEstudio()
    interfaz.ejecutar()

if __name__ == "__main__":
    main()