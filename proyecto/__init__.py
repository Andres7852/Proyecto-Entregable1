import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
import docx
import os
import random

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class EstudioPersonalizado:
    def __init__(self):
        self.documentos = []
        self.fichas = []
        self.stop_words = list(stopwords.words('spanish'))
        self.stop_words.extend([
            'a', 'al', 'algo', 'ante', 'con', 'de', 'del', 'desde', 'el', 'en', 'entre', 
            'hasta', 'la', 'las', 'lo', 'los', 'más', 'me', 'mi', 'mis', 'muy', 'nos', 
            'nuestro', 'nuestros', 'o', 'para', 'pero', 'por', 'que', 'se', 'sin', 'su', 
            'sus', 'te', 'ti', 'tu', 'un', 'una', 'y', 'ya'
        ])

    def generar_resumen(self, texto, num_oraciones=3):
        oraciones = sent_tokenize(texto)
        if len(oraciones) == 0:
            return "El texto está vacío."
        
        if len(oraciones) <= num_oraciones:
            return texto
        
        tfidf_vectorizer = TfidfVectorizer(stop_words=self.stop_words)
        tfidf_matrix = tfidf_vectorizer.fit_transform(oraciones)
        scores = tfidf_matrix.sum(axis=1).A1
        
        oraciones_ordenadas = sorted(zip(oraciones, scores), key=lambda x: x[1], reverse=True)
        resumen = [oracion for oracion, _ in oraciones_ordenadas[:num_oraciones]]
        
        return ' '.join(resumen)
    
    def extraer_conceptos_clave(self, texto, num_conceptos=5):
        tfidf_vectorizer = TfidfVectorizer(stop_words=self.stop_words)
        tfidf_matrix = tfidf_vectorizer.fit_transform([texto])
        palabras = tfidf_vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        conceptos = sorted(zip(palabras, scores), key=lambda x: x[1], reverse=True)
        conceptos_filtrados = [concepto[0] for concepto in conceptos if len(concepto[0]) > 2]
        
        return conceptos_filtrados[:num_conceptos]
    
    def generar_preguntas(self, texto, num_preguntas=5):
        conceptos = self.extraer_conceptos_clave(texto, num_conceptos=10)
        preguntas = []

        def definir_pregunta(concepto):
            return f"¿Qué es {concepto} en el contexto del documento?"

        def explicar_pregunta(concepto):
            return f"¿Cómo se utiliza {concepto} en el texto?"

        def comparar_pregunta(concepto):
            if len(conceptos) < 2:
                return f"¿Cómo se compara {concepto} con otro concepto en el texto?"
            otro_concepto = random.choice(conceptos)
            return f"¿Cómo se compara {concepto} con {otro_concepto}?"

        def aplicar_pregunta(concepto):
            return f"¿Cómo se aplica {concepto} en un contexto práctico?"

        tipos_pregunta = [
            definir_pregunta,
            explicar_pregunta,
            comparar_pregunta,
            aplicar_pregunta
        ]

        while len(preguntas) < num_preguntas and conceptos:
            tipo = random.choice(tipos_pregunta)
            concepto = random.choice(conceptos)
            conceptos.remove(concepto)

            if tipo == comparar_pregunta:
                pregunta = tipo(concepto)
                if "otro concepto" in pregunta:
                    continue
            else:
                pregunta = tipo(concepto)

            preguntas.append(pregunta)

        return preguntas

    def crear_ficha_hemerografica(self, texto):
        titulo = self.extraer_titulo(texto)
        contenido = f"Autor desconocido\n{titulo}\nRevista desconocida\nFecha desconocida\nNúmero desconocido\nCiudad y país desconocido\nFecha desconocida"
        ficha = self.Ficha("Hemerográfica", contenido)
        self.fichas.append(ficha)
        return self.fichas

    def crear_ficha_electronica(self, texto):
        titulo = self.extraer_titulo(texto)
        contenido = f"Autor desconocido\n{titulo}\nEditor desconocido\nURL desconocida\nFecha desconocida"
        ficha = self.Ficha("Electrónica", contenido)
        self.fichas.append(ficha)
        return self.fichas

    def crear_ficha_bibliografica(self, texto):
        titulo = self.extraer_titulo(texto)
        contenido = f"Autor desconocido\n{titulo}\nLugar de edición desconocido\nNúmero de páginas desconocido\nAño desconocido"
        ficha = self.Ficha("Bibliográfica", contenido)
        self.fichas.append(ficha)
        return self.fichas

    def crear_ficha_catalografica(self, texto):
        titulo = self.extraer_titulo(texto)
        contenido = f"Número desconocido\nMateria desconocida\nAutor desconocido\nTítulo: {titulo}\nDatos de edición desconocidos\nSinopsis desconocida\nDimensiones desconocidas\nNúmero de páginas desconocido"
        ficha = self.Ficha("Catalográfica", contenido)
        self.fichas.append(ficha)
        return self.fichas

    def crear_ficha_textual(self, texto):
        nota = self.generar_resumen(texto, 1)  # Usamos un resumen como nota
        contenido = f"Referencia bibliográfica desconocida\nClasificación desconocida\nNota: {nota}"
        ficha = self.Ficha("Textual", contenido)
        self.fichas.append(ficha)
        return self.fichas

    def crear_ficha_resumen(self, texto):
        ideas_principales = self.generar_resumen(texto, 3)
        contenido = f"Título desconocido\nAutor desconocido\nIdeas principales: {ideas_principales}\nReferencias desconocidas\nNotas desconocidas"
        ficha = self.Ficha("Resumen", contenido)
        self.fichas.append(ficha)
        return self.fichas

    def extraer_titulo(self, texto):
        oraciones = sent_tokenize(texto)
        if oraciones:
            return oraciones[0]  # Asumimos que la primera oración es el título
        return "Título desconocido"

    class Ficha:
        def __init__(self, tipo, contenido):
            self.tipo = tipo
            self.contenido = contenido

def leer_pdf(archivo_pdf):
    texto = ""
    try:
        with open(archivo_pdf, "rb") as file:
            lector_pdf = PyPDF2.PdfReader(file)
            for pagina in lector_pdf.pages:
                texto += pagina.extract_text() or ""
    except Exception as e:
        print(f"Error al leer el archivo PDF: {e}")
    return texto

def leer_docx(archivo_docx):
    texto = ""
    try:
        doc = docx.Document(archivo_docx)
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
    except Exception as e:
        print(f"Error al leer el archivo DOCX: {e}")
    return texto

def guardar_en_archivo(nombre_archivo, contenido):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        print(f"Contenido guardado en {nombre_archivo}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")

def interfaz_usuario():
    estudio = EstudioPersonalizado()
    
    print("Ingrese la ruta del archivo (pdf, docx):")
    ruta_archivo = input().strip()

    if not os.path.isfile(ruta_archivo):
        print("La ruta del archivo no es válida.")
        return

    if ruta_archivo.lower().endswith(".pdf"):
        texto = leer_pdf(ruta_archivo)
    elif ruta_archivo.lower().endswith(".docx"):
        texto = leer_docx(ruta_archivo)
    else:
        print("Formato de archivo no soportado.")
        return

    if not texto:
        print("El archivo está vacío o no se pudo leer.")
        return

    print("\nMuestra del texto leído:")
    print(texto[:1000])  # Mostrar los primeros 1000 caracteres para depuración

    print("\n¿Qué desea hacer con el documento?")
    print("1. Generar resumen")
    print("2. Extraer conceptos clave")
    print("3. Generar preguntas de estudio")
    print("4. Crear fichas de estudio")
    eleccion = input().strip()

    if eleccion == "1":
        resumen = estudio.generar_resumen(texto)
        print("\nResumen generado:")
        print(resumen)
        guardar_en_archivo("resumen.txt", resumen)
    
    elif eleccion == "2":
        conceptos_clave = estudio.extraer_conceptos_clave(texto)
        print("\nConceptos clave extraídos:")
        print(", ".join(conceptos_clave))
        guardar_en_archivo("conceptos_clave.txt", "\n".join(conceptos_clave))
    
    elif eleccion == "3":
        preguntas = estudio.generar_preguntas(texto)
        print("\nPreguntas generadas:")
        for pregunta in preguntas:
            print(pregunta)
        guardar_en_archivo("preguntas_estudio.txt", "\n".join(preguntas))
    
    elif eleccion == "4":
        print("\nCreando fichas de estudio...")
        estudio.crear_ficha_hemerografica(texto)
        estudio.crear_ficha_electronica(texto)
        estudio.crear_ficha_bibliografica(texto)
        estudio.crear_ficha_catalografica(texto)
        estudio.crear_ficha_textual(texto)
        estudio.crear_ficha_resumen(texto)
        
        for ficha in estudio.fichas:
            archivo_ficha = f"ficha_{ficha.tipo.lower()}.txt"
            guardar_en_archivo(archivo_ficha, ficha.contenido)
            print(f"Ficha {ficha.tipo} guardada en {archivo_ficha}")
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    interfaz_usuario()
