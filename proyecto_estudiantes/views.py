from models import Estudiante, CAMPOS_ESTUDIANTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

gestor = GestorJSON("data/estudiantes.json")

# TUPLAS de configuración: fijas, nadie las modifica en tiempo de ejecución
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")


# ===================== AYUDAS INTERNAS =====================

def carnets_registrados(excepto_id=None):
    """CONJUNTO con los carnets ya usados. Sirve para detectar duplicados al instante."""
    return {
        registro["carnet"].upper()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def emails_registrados(excepto_id=None):
    """CONJUNTO con los emails ya usados. Sirve para detectar duplicados al instante."""
    return {
        registro["email"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def siguiente_id():
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


# ===================== C · CREATE =====================

def crear_estudiante(datos):
    """datos: diccionario con las claves de CAMPOS_ESTUDIANTE. Devuelve (exito, mensaje)."""
    try:
        # 1) Normalizo: un diccionario con todos los campos, sin espacios sobrantes
        valores = {campo: str(datos.get(campo, "")).strip() for campo in CAMPOS_ESTUDIANTE}

        # 2) Reviso obligatorios recorriendo la TUPLA
        faltantes = [campo for campo in CAMPOS_OBLIGATORIOS if not valores[campo]]
        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

        # 3) Formato del email
        if not es_email_valido(valores["email"]):
            return False, f"El email '{valores['email']}' no tiene un formato válido"

        # 4) Duplicado de email: búsqueda instantánea dentro del CONJUNTO
        if valores["email"].lower() in emails_registrados():
            return False, "Ese email ya está registrado"

        # 5) Duplicado de carnet: búsqueda instantánea dentro del CONJUNTO
        if valores["carnet"].upper() in carnets_registrados():
            return False, "Ese carnet ya está registrado"

        # 6) Creo el objeto del Modelo. ** convierte el diccionario en argumentos
        estudiante = Estudiante(siguiente_id(), **valores)

        # 7) Agrego a la LISTA y guardo
        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return True, f"Estudiante {estudiante.obtener_nombre_completo()} creado con id {estudiante.id}"

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== R · READ =====================

def obtener_todos():
    """LISTA de objetos Estudiante."""
    return [Estudiante.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(id_estudiante):
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


# ===================== S · SEARCH =====================

def buscar_estudiantes(termino):
    """Búsqueda lineal: revisa registro por registro los campos de CAMPOS_BUSCABLES."""
    termino = termino.strip().lower()
    if not termino:
        return []

    encontrados = []
    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:                 # recorro la TUPLA de campos
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(Estudiante.desde_diccionario(registro))
                break                                   # ya coincidió: paso al siguiente estudiante
    return encontrados


# ===================== U · UPDATE =====================

def actualizar_estudiante(id_estudiante, cambios):
    """cambios: diccionario solo con los campos que se quieren modificar."""
    try:
        # DIFERENCIA DE CONJUNTOS: ¿mandaron algún campo que no existe?
        desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        if not cambios:
            return False, "No se indicó ningún cambio"

        if "email" in cambios:
            if not es_email_valido(cambios["email"]):
                return False, "El email no tiene un formato válido"
            if cambios["email"].lower() in emails_registrados(excepto_id=id_estudiante):
                return False, "Ese email ya lo usa otro estudiante"

        # Validación de carnet duplicado usando CONJUNTO
        if "carnet" in cambios:
            if cambios["carnet"].upper() in carnets_registrados(excepto_id=id_estudiante):
                return False, "Ese carnet ya lo usa otro estudiante"

        registros = gestor.leer()
        posicion = None
        for indice, registro in enumerate(registros):   # enumerate me da índice y valor
            if registro["id"] == id_estudiante:
                posicion = indice
                break

        if posicion is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        registros[posicion].update(cambios)             # actualizo el diccionario en su lugar
        gestor.guardar(registros)
        return True, f"Estudiante {id_estudiante} actualizado ({len(cambios)} campo/s)"

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== D · DELETE =====================

def eliminar_estudiante(id_estudiante):
    registros = gestor.leer()
    # Construyo una LISTA NUEVA sin ese registro: nunca borro mientras recorro
    quedan = [registro for registro in registros if registro["id"] != id_estudiante]

    if len(quedan) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"

    gestor.guardar(quedan)
    return True, f"Estudiante {id_estudiante} eliminado"


# ===================== EXTRA: funciones de la tarea =====================

def agregar_nota(id_estudiante, materia, nota):
    """Agrega una nota a un estudiante en una materia. Valida rango 0-20."""
    try:
        # Validar que la nota sea un número
        nota = float(nota)
    except (ValueError, TypeError):
        return False, "La nota debe ser un número"

    # Validar rango de la nota
    if nota < 0 or nota > 20:
        return False, f"La nota debe estar entre 0 y 20 (recibí {nota})"

    registros = gestor.leer()
    posicion = None
    for indice, registro in enumerate(registros):
        if registro["id"] == id_estudiante:
            posicion = indice
            break

    if posicion is None:
        return False, f"No existe un estudiante con id {id_estudiante}"

    # Uso el Modelo para agregar la nota correctamente
    estudiante = Estudiante.desde_diccionario(registros[posicion])
    estudiante.agregar_nota(materia, nota)

    # Actualizo el registro con los datos del objeto
    registros[posicion] = estudiante.a_diccionario()
    gestor.guardar(registros)

    return True, f"Nota {nota} agregada en {materia} para {estudiante.obtener_nombre_completo()}"


def materias_ofertadas():
    """Devuelve un CONJUNTO (set) con todas las materias inscritas por todos los estudiantes."""
    todas_materias = set()
    for registro in gestor.leer():
        # UNIÓN de conjuntos: voy acumulando todas las materias sin repetir
        todas_materias = todas_materias | set(registro.get("materias", []))
    return todas_materias


def estudiantes_en_comun(id_a, id_b):
    """Usa la INTERSECCIÓN de conjuntos para encontrar materias que comparten dos estudiantes."""
    estudiante_a = obtener_por_id(id_a)
    estudiante_b = obtener_por_id(id_b)

    if not estudiante_a:
        return False, f"No existe un estudiante con id {id_a}"
    if not estudiante_b:
        return False, f"No existe un estudiante con id {id_b}"

    # Usamos el método del Modelo que hace la intersección de conjuntos
    comunes = estudiante_a.materias_en_comun(estudiante_b)

    if not comunes:
        return True, (set(), estudiante_a, estudiante_b)

    return True, (comunes, estudiante_a, estudiante_b)
