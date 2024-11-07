from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import PyPDF2
import docx
import os
import random
import nltk
from typing import List, Optional
from datetime import datetime

class EstudioError(Exception):
    """Clase base para excepciones personalizadas del módulo"""
    pass

class DocumentoVacioError(EstudioError):
    """Se lanza cuando un documento está vacío"""
    pass

class ProcesamientoError(EstudioError):
    """Se lanza cuando hay un error en el procesamiento del texto"""
    pass

class EstudioPersonalizado:
    def __init__(self):
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            raise EstudioError(f"Error al inicializar NLTK: {str(e)}")
            
        self.documentos = []
        self.fichas = []
        self.stop_words = list(stopwords.words('spanish'))
        self.stop_words.extend([
            'a', 'al', 'algo', 'ante', 'con', 'de', 'del', 'desde', 'el', 'en', 'entre', 
            'hasta', 'la', 'las', 'lo', 'los', 'más', 'me', 'mi', 'mis', 'muy', 'nos', 
            'nuestro', 'nuestros', 'o', 'para', 'pero', 'por', 'que', 'se', 'sin', 'su', 
            'sus', 'te', 'ti', 'tu', 'un', 'una', 'y', 'ya'
        ])

    def validar_texto(self, texto: str) -> None:
        """Valida que el texto no esté vacío"""
        if not texto or not texto.strip():
            raise DocumentoVacioError("El texto proporcionado está vacío")

    def generar_resumen(self, texto: str, num_oraciones: int = 3) -> str:
        try:
            self.validar_texto(texto)
            oraciones = sent_tokenize(texto)
            
            if len(oraciones) <= num_oraciones:
                return texto
            
            tfidf_vectorizer = TfidfVectorizer(stop_words=self.stop_words)
            tfidf_matrix = tfidf_vectorizer.fit_transform(oraciones)
            scores = tfidf_matrix.sum(axis=1).A1
            
            oraciones_ordenadas = sorted(zip(oraciones, scores), key=lambda x: x[1], reverse=True)
            resumen = [oracion for oracion, _ in oraciones_ordenadas[:num_oraciones]]
            
            return ' '.join(resumen)
        except Exception as e:
            raise ProcesamientoError(f"Error al generar el resumen: {str(e)}")
    
    def extraer_conceptos_clave(self, texto: str, num_conceptos: int = 5) -> List[str]:
        try:
            self.validar_texto(texto)
            tfidf_vectorizer = TfidfVectorizer(stop_words=self.stop_words)
            tfidf_matrix = tfidf_vectorizer.fit_transform([texto])
            palabras = tfidf_vectorizer.get_feature_names_out()
            scores = tfidf_matrix.sum(axis=0).A1
            
            conceptos = sorted(zip(palabras, scores), key=lambda x: x[1], reverse=True)
            conceptos_filtrados = [concepto[0] for concepto in conceptos if len(concepto[0]) > 2]
            
            return conceptos_filtrados[:num_conceptos]
        except Exception as e:
            raise ProcesamientoError(f"Error al extraer conceptos clave: {str(e)}")

    def generar_preguntas(self, texto: str, num_preguntas: int = 5) -> List[str]:
        """
        Genera preguntas de estudio basadas en el texto proporcionado.
        
        Args:
            texto (str): Texto del cual generar preguntas
            num_preguntas (int): Número de preguntas a generar (default: 5)
            
        Returns:
            List[str]: Lista de preguntas generadas
        """
        try:
            self.validar_texto(texto)
            
            oraciones = sent_tokenize(texto)
            conceptos = self.extraer_conceptos_clave(texto, num_preguntas * 2)
            
            plantillas = [
                "¿Cuál es la importancia de {} en el texto?",
                "¿Qué relación existe entre {} y {}?",
                "¿Cómo se define o caracteriza {} en el contexto?",
                "¿Qué aspectos principales se mencionan sobre {}?",
                "¿Cuáles son las implicaciones de {} en el tema tratado?",
                "¿Por qué es relevante {} para la comprensión del texto?",
                "¿Qué ejemplos se presentan relacionados con {}?"
            ]
            
            preguntas = set()
            while len(preguntas) < num_preguntas and conceptos:
                plantilla = random.choice(plantillas)
                
                if "{}" in plantilla:
                    if plantilla.count("{}") == 2 and len(conceptos) >= 2:
                        concepto1 = conceptos.pop(0)
                        concepto2 = conceptos.pop(0)
                        pregunta = plantilla.format(concepto1, concepto2)
                    else:
                        concepto = conceptos.pop(0)
                        pregunta = plantilla.format(concepto)
                    
                    preguntas.add(pregunta)
            
            return list(preguntas)
        except Exception as e:
            raise ProcesamientoError(f"Error al generar preguntas: {str(e)}")

    def extraer_metadatos(self, texto: str) -> dict:
        """Extrae metadatos básicos del texto"""
        try:
            self.validar_texto(texto)
            titulo = self.extraer_titulo(texto)
            fecha_actual = datetime.now().strftime("%Y-%m-%d")
            conceptos = self.extraer_conceptos_clave(texto, 3)
            resumen_breve = self.generar_resumen(texto, 1)
            
            return {
                "titulo": titulo,
                "fecha_creacion": fecha_actual,
                "palabras_clave": conceptos,
                "resumen_breve": resumen_breve
            }
        except Exception as e:
            raise ProcesamientoError(f"Error al extraer metadatos: {str(e)}")

    class Ficha:
        def __init__(self, tipo: str, contenido: str, metadatos: dict):
            self.tipo = tipo
            self.contenido = contenido
            self.metadatos = metadatos
            self.fecha_creacion = datetime.now().strftime("%Y-%m-%d")

        def __str__(self) -> str:
            return f"""
Tipo de ficha: {self.tipo}
Fecha de creación: {self.fecha_creacion}
Título: {self.metadatos.get('titulo', 'No disponible')}
Palabras clave: {', '.join(self.metadatos.get('palabras_clave', []))}
------------------------
{self.contenido}
"""

    def crear_ficha_hemerografica(self, texto: str) -> Optional[Ficha]:
        try:
            metadatos = self.extraer_metadatos(texto)
            contenido = f"""
Título: {metadatos['titulo']}
Autor: No especificado
Revista/Periódico: No especificado
Fecha de publicación: No especificada
Número/Volumen: No especificado
Ciudad y país: No especificado
Palabras clave: {', '.join(metadatos['palabras_clave'])}
Resumen: {metadatos['resumen_breve']}"""
            
            ficha = self.Ficha("Hemerográfica", contenido, metadatos)
            self.fichas.append(ficha)
            return ficha
        except Exception as e:
            raise ProcesamientoError(f"Error al crear ficha hemerográfica: {str(e)}")

    def crear_ficha_electronica(self, texto: str) -> Optional[Ficha]:
        try:
            metadatos = self.extraer_metadatos(texto)
            contenido = f"""
Título: {metadatos['titulo']}
Autor: No especificado
Editor/Sitio web: No especificado
URL: No especificada
Fecha de acceso: {datetime.now().strftime("%Y-%m-%d")}
Palabras clave: {', '.join(metadatos['palabras_clave'])}
Resumen: {metadatos['resumen_breve']}"""
            
            ficha = self.Ficha("Electrónica", contenido, metadatos)
            self.fichas.append(ficha)
            return ficha
        except Exception as e:
            raise ProcesamientoError(f"Error al crear ficha electrónica: {str(e)}")

    def crear_ficha_bibliografica(self, texto: str) -> Optional[Ficha]:
        try:
            metadatos = self.extraer_metadatos(texto)
            contenido = f"""
Título: {metadatos['titulo']}
Autor: No especificado
Lugar de edición: No especificado
Editorial: No especificada
Año: No especificado
ISBN: No especificado
Palabras clave: {', '.join(metadatos['palabras_clave'])}
Resumen: {metadatos['resumen_breve']}"""
            
            ficha = self.Ficha("Bibliográfica", contenido, metadatos)
            self.fichas.append(ficha)
            return ficha
        except Exception as e:
            raise ProcesamientoError(f"Error al crear ficha bibliográfica: {str(e)}")

    def crear_ficha_catalografica(self, texto: str) -> Optional[Ficha]:
        try:
            metadatos = self.extraer_metadatos(texto)
            contenido = f"""
Número de clasificación: No especificado
Materia: {', '.join(metadatos['palabras_clave'])}
Autor: No especificado
Título: {metadatos['titulo']}
Datos de edición: No especificados
Descripción física: No especificada
Notas: {metadatos['resumen_breve']}
Localización: No especificada"""
            
            ficha = self.Ficha("Catalográfica", contenido, metadatos)
            self.fichas.append(ficha)
            return ficha
        except Exception as e:
            raise ProcesamientoError(f"Error al crear ficha catalográfica: {str(e)}")

    def crear_ficha_textual(self, texto: str) -> Optional[Ficha]:
        try:
            metadatos = self.extraer_metadatos(texto)
            contenido = f"""
Referencia bibliográfica: No especificada
Clasificación: No especificada
Cita textual: {metadatos['resumen_breve']}
Palabras clave: {', '.join(metadatos['palabras_clave'])}
Comentarios: No especificados"""
            
            ficha = self.Ficha("Textual", contenido, metadatos)
            self.fichas.append(ficha)
            return ficha
        except Exception as e:
            raise ProcesamientoError(f"Error al crear ficha textual: {str(e)}")

    def crear_ficha_resumen(self, texto: str) -> Optional[Ficha]:
        try:
            metadatos = self.extraer_metadatos(texto)
            resumen_completo = self.generar_resumen(texto, 3)
            contenido = f"""
Título: {metadatos['titulo']}
Autor: No especificado
Palabras clave: {', '.join(metadatos['palabras_clave'])}
Ideas principales:
{resumen_completo}
Referencias: No especificadas
Notas adicionales: No especificadas"""
            
            ficha = self.Ficha("Resumen", contenido, metadatos)
            self.fichas.append(ficha)
            return ficha
        except Exception as e:
            raise ProcesamientoError(f"Error al crear ficha resumen: {str(e)}")

    def extraer_titulo(self, texto: str) -> str:
        try:
            self.validar_texto(texto)
            oraciones = sent_tokenize(texto)
            if oraciones:
                titulo = oraciones[0].strip()
                return titulo[:100] if len(titulo) > 100 else titulo
            return "Título no disponible"
        except Exception as e:
            raise ProcesamientoError(f"Error al extraer título: {str(e)}")

def leer_pdf(archivo_pdf: str) -> str:
    try:
        texto = ""
        with open(archivo_pdf, "rb") as file:
            lector_pdf = PyPDF2.PdfReader(file)
            for pagina in lector_pdf.pages:
                texto += pagina.extract_text() or ""
        if not texto.strip():
            raise DocumentoVacioError("El archivo PDF está vacío o no contiene texto extraíble")
        return texto
    except DocumentoVacioError:
        raise
    except Exception as e:
        raise EstudioError(f"Error al leer el archivo PDF: {str(e)}")

def leer_docx(archivo_docx: str) -> str:
    try:
        texto = ""
        doc = docx.Document(archivo_docx)
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
        if not texto.strip():
            raise DocumentoVacioError("El archivo DOCX está vacío o no contiene texto")
        return texto
    except DocumentoVacioError:
        raise
    except Exception as e:
        raise EstudioError(f"Error al leer el archivo DOCX: {str(e)}")

def guardar_en_archivo(nombre_archivo: str, contenido: str) -> None:
    try:
        directorio = "fichas_generadas"
        if not os.path.exists(directorio):
            os.makedirs(directorio)
            
        ruta_completa = os.path.join(directorio, nombre_archivo)
        with open(ruta_completa, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        print(f"✓ Contenido guardado en {ruta_completa}")
    except Exception as e:
        raise EstudioError(f"Error al guardar el archivo: {str(e)}")

def interfaz_usuario():
    try:
        estudio = EstudioPersonalizado()
        
        print("\n=== Sistema de Estudio Personalizado ===")
        print("Ingrese la ruta del archivo (PDF o DOCX):")
        ruta_archivo = input().strip()

        if not os.path.isfile(ruta_archivo):
            raise FileNotFoundError("La ruta del archivo no es válida.")

        extension = os.path.splitext(ruta_archivo)[1].lower()
        if extension == '.pdf':
            texto = leer_pdf(ruta_archivo)
        elif extension == '.docx':
            texto = leer_docx(ruta_archivo)
        else:
            raise ValueError("Formato de archivo no soportado. Use PDF o DOCX.")

        print("\n=== Opciones disponibles ===")
        print("1. Generar resumen")
        print("2. Extraer conceptos clave")
        print("3. Generar preguntas de estudio")
        print("4. Crear fichas de estudio")
        print("\nSeleccione una opción (1-4):")
        
        eleccion = input().strip()

        if eleccion == "1":
            resumen = estudio.generar_resumen(texto)
            print("\n=== Resumen generado ===")
            print(resumen)
            guardar_en_archivo("resumen.txt", resumen)
        
        elif eleccion == "2":
            conceptos_clave = estudio.extraer_conceptos_clave(texto)
            print("\n=== Conceptos clave ===")
            print("• " + "\n• ".join(conceptos_clave))
            guardar_en_archivo("conceptos_clave.txt", "\n".join(conceptos_clave))
        
        elif eleccion == "3":
            preguntas = estudio.generar_preguntas(texto)
            print("\n=== Preguntas de estudio ===")
            for i, pregunta in enumerate(preguntas, 1):
                print(f"{i}. {pregunta}")
            guardar_en_archivo("preguntas_estudio.txt", "\n".join(preguntas))
        
        elif eleccion == "4":
            print("\n=== Generando fichas de estudio ===")
            tipos_fichas = {
                "hemerografica": estudio.crear_ficha_hemerografica,
                "electronica": estudio.crear_ficha_electronica,
                "bibliografica": estudio.crear_ficha_bibliografica,
                "catalografica": estudio.crear_ficha_catalografica,
                "textual": estudio.crear_ficha_textual,
                "resumen": estudio.crear_ficha_resumen
            }
            
            for tipo, funcion in tipos_fichas.items():
                try:
                    ficha = funcion(texto)
                    if ficha:
                        nombre_archivo = f"ficha_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        guardar_en_archivo(nombre_archivo, str(ficha))
                except ProcesamientoError as e:
                    print(f"⚠ Error al crear ficha {tipo}: {str(e)}")
                    continue
            
            print("\n✓ Proceso de generación de fichas completado")
        else:
            print("\n⚠ Opción no válida. Por favor, seleccione una opción del 1 al 4.")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}")
        print("Asegúrese de que el archivo existe y la ruta es correcta.")
    except DocumentoVacioError as e:
        print(f"\n❌ Error: {str(e)}")
        print("El documento no contiene texto que pueda ser procesado.")
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
        print("Formatos soportados: PDF (.pdf) y Word (.docx)")
    except EstudioError as e:
        print(f"\n❌ Error en el procesamiento: {str(e)}")
        print("Por favor, verifique el contenido del archivo e intente nuevamente.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        print("Por favor, contacte al soporte técnico si el problema persiste.")
    finally:
        print("\n=== Fin del proceso ===")

if __name__ == "__main__":
    interfaz_usuario()