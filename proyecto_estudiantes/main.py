from models import CAMPOS_ESTUDIANTE
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import (
    crear_estudiante, obtener_todos, obtener_por_id, buscar_estudiantes,
    actualizar_estudiante, eliminar_estudiante,
    agregar_nota, materias_ofertadas, estudiantes_en_comun
)


def pausa():
    input("\nPresione Enter para continuar...")


def mostrar_tabla(estudiantes):
    print(f"{'ID':<5}{'NOMBRE':<25}{'EMAIL':<28}{'CARNET':<15}{'PROMEDIO':<10}")
    print("-" * 83)
    for est in estudiantes:
        print(f"{est.id:<5}{est.obtener_nombre_completo():<25}"
              f"{est.email:<28}{est.carnet:<15}{est.obtener_promedio():<10}")
    print("-" * 83)
    imprimir_info(f"Total: {len(estudiantes)} estudiante(s)")


# ---------- C · CREAR ----------
def opcion_crear():
    imprimir_titulo("CREAR NUEVO ESTUDIANTE")
    # Recorro la TUPLA de campos: si mañana agrego un campo al Modelo,
    # este formulario se actualiza solo.
    datos = {}
    for campo in CAMPOS_ESTUDIANTE:
        datos[campo] = input(f"{campo.capitalize()}: ")

    exito, mensaje = crear_estudiante(datos)          # desempaqueto la TUPLA que devuelve
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ---------- R · LEER TODOS ----------
def opcion_ver_todos():
    imprimir_titulo("LISTA DE ESTUDIANTES")
    estudiantes = obtener_todos()
    if not estudiantes:
        imprimir_info("Todavía no hay estudiantes. Use la opción 1 para crear el primero.")
    else:
        mostrar_tabla(estudiantes)
    pausa()


# ---------- S · BUSCAR ----------
def opcion_buscar():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, email o carnet: ")
    encontrados = buscar_estudiantes(termino)

    if not encontrados:
        imprimir_info(f"Ningún estudiante coincide con '{termino}'.")
    else:
        mostrar_tabla(encontrados)
    pausa()


# ---------- R · LEER UNO ----------
def opcion_ver_por_id():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
    else:
        # Recorro el DICCIONARIO del estudiante: clave y valor a la vez
        for clave, valor in estudiante.a_diccionario().items():
            print(f"  {clave.capitalize():<12}: {valor}")
    pausa()


# ---------- U · ACTUALIZAR ----------
def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()

    imprimir_info(f"Editando a {estudiante.obtener_nombre_completo()}")
    print("Deje en blanco el campo que no quiera cambiar.\n")

    # Armo un DICCIONARIO solo con lo que el usuario escribió
    cambios = {}
    for campo in CAMPOS_ESTUDIANTE:
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    exito, mensaje = actualizar_estudiante(id_estudiante, cambios)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ---------- D · ELIMINAR ----------
def opcion_eliminar():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()

    imprimir_info(f"Se eliminará: {estudiante}")
    if confirmar("¿Confirma la eliminación?"):
        exito, mensaje = eliminar_estudiante(id_estudiante)
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)
    else:
        imprimir_info("Operación cancelada")
    pausa()


# ---------- EXTRA · AGREGAR NOTA ----------
def opcion_agregar_nota():
    imprimir_titulo("AGREGAR NOTA")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()

    imprimir_info(f"Estudiante: {estudiante.obtener_nombre_completo()}")
    materia = input("Materia: ").strip()
    if not materia:
        imprimir_error("La materia no puede estar vacía")
        return pausa()

    nota_texto = input("Nota (0-20): ").strip()

    exito, mensaje = agregar_nota(id_estudiante, materia, nota_texto)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ---------- EXTRA · VER PROMEDIO ----------
def opcion_ver_promedio():
    imprimir_titulo("VER PROMEDIO DE ESTUDIANTE")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número entero")
        return pausa()

    estudiante = obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return pausa()

    imprimir_info(f"Estudiante: {estudiante.obtener_nombre_completo()} ({estudiante.carnet})")
    print()

    if not estudiante.notas:
        imprimir_info("Este estudiante no tiene notas registradas.")
    else:
        # Recorro el DICCIONARIO de notas: materia -> lista de notas
        print(f"  {'MATERIA':<20}{'NOTAS':<30}{'PROMEDIO':<10}")
        print("  " + "-" * 60)
        for materia, lista_notas in estudiante.notas.items():
            notas_str = ", ".join(str(n) for n in lista_notas)
            promedio_materia = round(sum(lista_notas) / len(lista_notas), 2)
            print(f"  {materia:<20}{notas_str:<30}{promedio_materia:<10}")
        print("  " + "-" * 60)
        imprimir_exito(f"Promedio general: {estudiante.obtener_promedio()}")

    # Mostrar materias inscritas (CONJUNTO)
    if estudiante.materias:
        print(f"\n  Materias inscritas: {', '.join(sorted(estudiante.materias))}")
    pausa()


# ---------- EXTRA · MATERIAS EN COMÚN ----------
def opcion_materias_en_comun():
    imprimir_titulo("MATERIAS EN COMÚN")
    try:
        id_a = int(input("Id del primer estudiante: "))
        id_b = int(input("Id del segundo estudiante: "))
    except ValueError:
        imprimir_error("Los ids deben ser números enteros")
        return pausa()

    exito, resultado = estudiantes_en_comun(id_a, id_b)

    if not exito:
        # resultado es el mensaje de error
        imprimir_error(resultado)
    else:
        comunes, est_a, est_b = resultado
        imprimir_info(f"Estudiante A: {est_a.obtener_nombre_completo()} - Materias: {sorted(est_a.materias)}")
        imprimir_info(f"Estudiante B: {est_b.obtener_nombre_completo()} - Materias: {sorted(est_b.materias)}")
        print()
        if comunes:
            imprimir_exito(f"Materias en común (intersección): {sorted(comunes)}")
        else:
            imprimir_info("No comparten ninguna materia.")
    pausa()


def salir():
    imprimir_info("¡Hasta luego! 👋")
    return "salir"


# DICCIONARIO de opciones: tecla -> (texto del menú, función)
OPCIONES = {
    "1": ("Crear estudiante", opcion_crear),
    "2": ("Ver todos", opcion_ver_todos),
    "3": ("Buscar", opcion_buscar),
    "4": ("Ver por id", opcion_ver_por_id),
    "5": ("Actualizar", opcion_actualizar),
    "6": ("Eliminar", opcion_eliminar),
    "7": ("Agregar nota", opcion_agregar_nota),
    "8": ("Ver promedio", opcion_ver_promedio),
    "9": ("Materias en común", opcion_materias_en_comun),
    "0": ("Salir", salir),
}


def mostrar_menu():
    imprimir_titulo("SISTEMA DE GESTIÓN DE ESTUDIANTES")
    for tecla, (texto, _funcion) in OPCIONES.items():
        print(f"  {tecla}. {texto}")
    print()


def main():
    while True:
        mostrar_menu()
        tecla = input("Seleccione una opción: ").strip()

        if tecla not in OPCIONES:          # búsqueda instantánea por clave
            imprimir_error("Opción no válida")
            pausa()
            continue

        _texto, funcion = OPCIONES[tecla]
        if funcion() == "salir":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
