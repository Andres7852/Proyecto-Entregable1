# interfaz.py
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from proyecto.app import EstudioPersonalizado, leer_docx, leer_pdf


def interfaz_usuario():
    def cargar_archivo():
        archivo = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf"), ("Archivos DOCX", "*.docx")])
        if archivo:
            texto = ""
            if archivo.lower().endswith(".pdf"):
                texto = leer_pdf(archivo)
            elif archivo.lower().endswith(".docx"):
                texto = leer_docx(archivo)
            if texto:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, texto[:1000])  # Muestra los primeros 1000 caracteres
            else:
                messagebox.showerror("Error", "No se pudo leer el archivo.")
        else:
            messagebox.showerror("Error", "No se seleccionó ningún archivo.")
    
    def mostrar_resumen():
        texto = text_area.get(1.0, tk.END).strip()
        if texto:
            resumen = estudio.generar_resumen(texto)
            result_area.delete(1.0, tk.END)
            result_area.insert(tk.END, resumen)
        else:
            messagebox.showerror("Error", "No hay texto cargado.")
    
    def mostrar_conceptos_clave():
        texto = text_area.get(1.0, tk.END).strip()
        if texto:
            conceptos = estudio.extraer_conceptos_clave(texto)
            result_area.delete(1.0, tk.END)
            result_area.insert(tk.END, "\n".join(conceptos))
        else:
            messagebox.showerror("Error", "No hay texto cargado.")
    
    def mostrar_preguntas():
        texto = text_area.get(1.0, tk.END).strip()
        if texto:
            preguntas = estudio.generar_preguntas(texto)
            result_area.delete(1.0, tk.END)
            result_area.insert(tk.END, "\n".join(preguntas))
        else:
            messagebox.showerror("Error", "No hay texto cargado.")
    
    def mostrar_fichas_estudio():
        texto = text_area.get(1.0, tk.END).strip()
        if texto:
            fichas = estudio.generar_fichas_estudio(texto)
            result_area.delete(1.0, tk.END)
            for ficha in fichas:
                result_area.insert(tk.END, f"Concepto: {ficha['Concepto']}\nPregunta: {ficha['Pregunta']}\n\n")
        else:
            messagebox.showerror("Error", "No hay texto cargado.")
    
    estudio = EstudioPersonalizado()
    
    # Configuración de la ventana principal
    root = tk.Tk()
    root.title("Estudio Personalizado")
    
    # Área de texto para mostrar el contenido cargado
    text_area = scrolledtext.ScrolledText(root, width=80, height=10)
    text_area.pack(padx=10, pady=10)
    
    # Botones para realizar las operaciones
    load_button = tk.Button(root, text="Cargar Documento", command=cargar_archivo)
    load_button.pack(padx=10, pady=5)

    resumen_button = tk.Button(root, text="Generar Resumen", command=mostrar_resumen)
    resumen_button.pack(padx=10, pady=5)

    conceptos_button = tk.Button(root, text="Conceptos Clave", command=mostrar_conceptos_clave)
    conceptos_button.pack(padx=10, pady=5)

    preguntas_button = tk.Button(root, text="Generar Preguntas", command=mostrar_preguntas)
    preguntas_button.pack(padx=10, pady=5)

    fichas_button = tk.Button(root, text="Generar Fichas de Estudio", command=mostrar_fichas_estudio)
    fichas_button.pack(padx=10, pady=5)
    
    result_area = scrolledtext.ScrolledText(root, width=80, height=20)
    result_area.pack(padx=10, pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    interfaz_usuario()
    
