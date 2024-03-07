import spacy
from spacy.matcher import DependencyMatcher
from spacy.matcher import Matcher
from spacy import displacy
import pdfplumber

# La tarea extra consiste en: Extraer la información mas importante, 
# como hablamos hoy de un escrito judicial. El escrito judicial que les voy
# a pasar es de la materia contencioso administrativo/ tributario. Lo mas importante
# que tienen que hacer es, extraer justamente la materia (Pista: mirar a lo ultimo 
# de todo). y ademas si pueden y quieren pueden extraer cosas interesantes como: Quien esta involucrado / personas 
# (pueden usar entidades), extraer fechas (pista tienen que retocar el shape o buscar el patron directamente de fechas),
# y el resultado (que es lo que hace la corte, por ejemplo si acepta o "declara admisible" 

# Cargamos modelo
nlp = spacy.load("es_core_news_sm")

# Cargamos matcher
matcher = DependencyMatcher(nlp.vocab)
matcher.add("patronJuzgado", [
    [
        # Anclamos "juzgado" como base, con "lower" no discrimina con case sensitive
        {"RIGHT_ID": "Juzgado", "RIGHT_ATTRS": {"lower": "juzgado"}},
        # Con LEFT_ID nos anclamos a "juzgado" para la próxima palabra a buscar, luego con REL_OP decimos que es siguiente a "juzgado"
        {"LEFT_ID": "Juzgado", "REL_OP": ">", "RIGHT_ID": "Contencioso", "RIGHT_ATTRS": {"DEP": "nmod"}},
        # Ahora nos quedamos con "administrativo" que está inmediatamente siguiente
        {"LEFT_ID": "Contencioso", "REL_OP": ".", "RIGHT_ID": "Administrativo", "RIGHT_ATTRS": {"DEP": "flat"}}
    ]
]
)

matcher.add("patronDeclaracion", [
    [
        # Con el LEMMA busca el verbo "declarar" en sus diferentes conjugaciones
        {"RIGHT_ID": "declara", "RIGHT_ATTRS": {"LEMMA": "declarar", "POS": "VERB"}},
        {"LEFT_ID": "declara", "REL_OP": ">", "RIGHT_ID": "admisible", "RIGHT_ATTRS": {"DEP": "adj"}},
        # Con el REl_OP ">>" busca el "se" antes del verbo declarar
        {"LEFT_ID": "declara", "REL_OP": ">", "RIGHT_ID": "se", "RIGHT_ATTRS": {"DEP": "aux"}}
    ]
])


# Inicializamos el matcher
matcher_fecha = Matcher(nlp.vocab)

# Definimos el patrón para fechas SHAPE
matcher_fecha.add("FECHA", [
     [
    {"POS": "NUM"},           # Día
    {"LOWER": "de"},          # "de"
    {"POS": "NOUN"},          # Mes
    {"LOWER": "de"},          # "de"
    {"POS": "NUM"},           # Año
    ]
]
)

def obtener_texto(nombre_archivo): 
    texto = ""
    with pdfplumber.open(nombre_archivo) as pdf:
        for page in pdf.pages:
            texto += page.extract_text()
    return texto

def extraer_materia(doc):

    # Aplicamos el matcher
    coincidencias = matcher(doc)

    # Vemos el resultado

    # [(12098889199307091093, [0, 7, 8])] formato de coincidencias
    for match_id, token_ids in coincidencias:
        palabra= []
        # Ahora por cada id de coincidencia, los ordenamos para que las palabras salgan en orden
        for token_id in sorted(token_ids):
            # Guardamos el token i
            token = doc[token_id]
            # Lo vamos guardando como texto en la lista
            palabra.append(token.text)
        # Agregamos los elementos a un solo string
        palabra = " ".join(palabra)

    # Vemos en displacy
    # displacy.serve(doc)
            
    return palabra
    
    
def extraer_fechas(doc):

    # Aplicamos el matcher al documento
    matches = matcher_fecha(doc)

    # Extraemos las fechas encontradas17 de Junio de 2021
    fechas_encontradas = []
    for match_id, start, end in matches:
        fecha = doc[start:end]
        fechas_encontradas.append(fecha.text)

    return fechas_encontradas

def extraer_declaracion(doc):
    
    coincidencias = matcher(doc)

    palabra = []

    for match_id, token_ids in coincidencias:
        if match_id == "patronDeclaracion":
            for token_id in sorted(token_ids):
                token = doc[token_id]
                palabra.append(token.text)
            palabra = " ".join(palabra)
                   
    return palabra

def extraer_entidades(doc):
    personas = []
    
    for token in doc.ents:
        if token.label_ == "PER":
            personas.append(token.text)
    
    return personas
    

texto = obtener_texto("textoJudicial.pdf")
doc = nlp(texto)
materia = extraer_materia(doc)
fechas = extraer_fechas(doc)
declaracion = extraer_declaracion(doc)
personas = extraer_entidades(doc)
print("_"*100,"\n")
print("Materia del caso -> ",materia)
print("Fechas encontradas -> ", fechas)
print("Declaración del caso -> ", declaracion)
print("Personas involucradas -> ", personas)
print("_"*100,"\n")