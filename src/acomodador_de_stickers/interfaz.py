from dataclasses import dataclass
import os
import cv2
import dearpygui.dearpygui as dpg
import numpy as np
from src.acomodador_de_stickers.utils import hojas
from src.acomodador_de_stickers.acomodador import (
    Imagen,
    Acomodador,
    escalar_imagen,
    cuadrar_imagen,
)

opciones_hojas = [f"{key}: {val[0]}mm x {val[1]}mm" for key, val in hojas.items()]
VERSION="v0.1.0"

ANCHO_VENTANA = 880
ALTO_VENTANA = 660
ANCHO_PLANTILLA = 420
ALTO_PLANTILLA = 594
TAM_IMG = 100


@dataclass
class Opciones:
    acomodo: str
    tam_hoja: str
    margenes: list
    imagen: str
    dpi: int
    forma: str
    cantidad: int
    nombre: str

    def __init__(self):
        self.imagen = ""
        self.acomodo = "ancho"
        self.tam_hoja = "A4"
        self.margenes = [0, 0, 0, 0]
        self.dpi = 300
        self.forma = "rectangular"
        self.cantidad = 6
        self.nombre="plantilla.png"


class Display:
    acomodador: Acomodador
    imagen: Imagen


opciones = Opciones()
display = Display()

def callback_hoja(sender, data):
    opciones.tam_hoja = dpg.get_value(sender)[:2]


def callback_cantidad(sender, data):
    opciones.cantidad = dpg.get_value(sender)


def callback_acomodo(sender, data):
    opciones.acomodo = dpg.get_value(sender)


def callback_margen_arr(sender, data):
    opciones.margenes[0] = dpg.get_value(sender)


def callback_margen_der(sender, data):
    opciones.margenes[1] = dpg.get_value(sender)


def callback_margen_aba(sender, data):
    opciones.margenes[2] = dpg.get_value(sender)


def callback_margen_izq(sender, data):
    opciones.margenes[3] = dpg.get_value(sender)


def callback_dpi(sender, data):
    opciones.dpi = dpg.get_value(sender)


def cancel_callback(sender, app_data):
    print("Cancel was clicked.")
    print("Sender: ", sender)
    print("App Data: ", app_data)


def callback_crear_hoja(sender, app_data):
    ancho, alto = hojas[opciones.tam_hoja]
    display.acomodador = Acomodador(
        alto=alto, ancho=ancho, margenes=opciones.margenes, dpi=opciones.dpi
    )
    margenes = opciones.margenes
    imagen_ok = getattr(display, "imagen", None) is not None
    cantidad_ok = opciones.cantidad > 0
    margenes_ok = (margenes[0] + margenes[2]) < alto and (margenes[1] + margenes[3]) < ancho
    if imagen_ok and cantidad_ok and margenes_ok:
        if opciones.forma == "rectangular":
            display.acomodador.acomodar_rectangular(
                display.imagen, opciones.acomodo, opciones.cantidad
            )
        elif opciones.forma == "circular":
            display.acomodador.acomodar_circular(
                display.imagen, opciones.acomodo, opciones.cantidad
            )
        nueva = np.ones((ALTO_PLANTILLA, ANCHO_PLANTILLA, 4), dtype=np.float32)
        plantilla = cv2.cvtColor(display.acomodador.plantilla, cv2.COLOR_BGR2RGB)
        nueva[:, :, :3] = (
            escalar_imagen(plantilla, ALTO_PLANTILLA, ANCHO_PLANTILLA) / 255
        )
        dpg.set_value("textura_plantilla", nueva.flatten().tolist())
        dpg.configure_item("nombre_hoja", show=True)
        dpg.configure_item("descargar_hoja", show=True)
        dpg.configure_item("estado", default_value="Hoja creada")
    else:
        if not imagen_ok:
            dpg.configure_item(
                "estado",
                default_value="Error: Carga imagen",
            )
        if not cantidad_ok:
            dpg.configure_item(
                "estado",
                default_value="Error: Revisar la cantidad",
            )
        if not margenes_ok:
            dpg.configure_item(
                "estado",
                default_value="Error: Márgenes incorrectos",
            )

def callback_nombre_hoja(sender, app_data):
    opciones.nombre = dpg.get_value(sender)
    dpg.configure_item("nombre_hoja", default_value=opciones.nombre)


def callback_descargar_hoja(sender, app_data):
    imagen = cv2.cvtColor(display.acomodador.plantilla, cv2.COLOR_BGR2RGB)
    forma = display.acomodador.plantilla.shape
    if opciones.nombre.endswith(".png") or opciones.nombre.endswith(".jpg"):
        dpg.save_image(
            file=opciones.nombre, width=forma[1], height=forma[0], data=imagen, components=3
        )
        dpg.configure_item(
            "estado",
            default_value=f"Plantilla guardada en {os.path.join(os.getcwd(), opciones.nombre)}",
        )
    else:
        dpg.configure_item(
            "estado",
            default_value="Plantilla no guardada, usa png o jpg",
        )


def callback_forma(sender, app_data):
    opciones.forma = dpg.get_value(sender)


def crear_textura(alto: int, ancho: int):
    textura = []
    for j in range(alto):
        for i in range(ancho):
            textura.extend([1.0, 1.0, 1.0, 1.0])
    return textura


def agregar_margenes():
    dpg.add_text("Márgenes (mm)")
    dpg.add_input_int(
        label="Arriba",
        default_value=0,
        width=100,
        callback=callback_margen_arr,
        min_value=0,
        min_clamped=True,
    )
    dpg.add_input_int(
        label="Derecha",
        default_value=0,
        width=100,
        callback=callback_margen_der,
        min_value=0,
        min_clamped=True,
    )
    dpg.add_input_int(
        label="Izquierda",
        default_value=0,
        width=100,
        callback=callback_margen_aba,
        min_value=0,
        min_clamped=True,
    )
    dpg.add_input_int(
        label="Arriba",
        default_value=0,
        width=100,
        callback=callback_margen_izq,
        min_value=0,
        min_clamped=True,
    )


def agregar_opciones():
    dpg.add_combo(
        tag="Hojas",
        items=opciones_hojas,
        callback=callback_hoja,
        label="Tamaño de hoja",
        width=150,
        default_value=opciones_hojas[4],
    )
    dpg.add_input_int(
        label="Cantidad de stickers(ancho o alto)",
        default_value=6,
        width=100,
        min_value=1,
        max_value=200,
        min_clamped=True,
        max_clamped=True,
        callback=callback_cantidad,
    )
    dpg.add_combo(
        tag="Acomodo",
        items=["ancho", "alto"],
        callback=callback_acomodo,
        default_value="ancho",
        label="Acomodar",
        width=150,
    )
    dpg.add_combo(
        tag="Forma",
        items=["rectangular", "circular"],
        callback=callback_forma,
        default_value="rectangular",
        label="Forma de sticker",
        width=150,
    )


def callback_dir(sender, app_data):
    opciones.imagen = app_data["file_path_name"]
    display.imagen = Imagen(opciones.imagen)
    cuadrada = cuadrar_imagen(display.imagen.imagen)
    tam = cuadrada.shape[0]
    escalada = display.imagen.escalar_imagen(TAM_IMG / tam)
    escalada = cv2.cvtColor(escalada, cv2.COLOR_BGR2RGB)
    nueva = np.ones((TAM_IMG, TAM_IMG, 4), dtype=np.float32)
    nueva[:, :, :3] = escalada / 255
    dpg.set_value("textura_imagen", nueva.flatten().tolist())
    dpg.configure_item(
        "estado", default_value=f"Imagen {app_data['file_path_name']} cargada"
    )


def agregar_dialogo_directorio():
    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=callback_dir,
        tag="archivo",
        cancel_callback=cancel_callback,
        width=700,
        height=400,
    ):
        dpg.add_file_extension(".png")
        dpg.add_file_extension(".jpg")


dpg.create_context()

with dpg.font_registry():
    fuente = dpg.add_font("fuente/OpenSans-Regular.ttf", 18)
   
dpg.bind_font(fuente)

textura_plantilla = crear_textura(ALTO_PLANTILLA, ANCHO_PLANTILLA)
with dpg.texture_registry():
    dpg.add_dynamic_texture(
        width=ANCHO_PLANTILLA,
        height=ALTO_PLANTILLA,
        default_value=textura_plantilla,
        tag="textura_plantilla",
    )

textura_imagen = crear_textura(TAM_IMG, TAM_IMG)
with dpg.texture_registry():
    dpg.add_dynamic_texture(
        width=TAM_IMG,
        height=TAM_IMG,
        default_value=textura_imagen,
        tag="textura_imagen",
    )


def crear_interfaz():
    agregar_dialogo_directorio()
    with dpg.window(tag="Ventana Primaria", label="Acomodador de stickers"):
        dpg.add_button(
            label="Elegir imagen",
            callback=lambda: dpg.show_item("archivo"),
            width=100,
            height=30,
        )
        dpg.add_image("textura_imagen", label="imagen")
        dpg.add_text("Opciones")
        agregar_opciones()
        agregar_margenes()

        dpg.add_input_int(
            label="DPI", default_value=300, width=100, callback=callback_dpi
        )
        dpg.add_button(
            label="Crear hoja",
            callback=callback_crear_hoja,
            width=100,
            height=30,
        )
        dpg.add_input_text(
            default_value=opciones.nombre,
            label="Nombre",
            tag="nombre_hoja",
            callback=callback_nombre_hoja,
            width=200,
            height=30,
            show=False,
        )
        dpg.add_button(
            label="Guardar hoja",
            callback=callback_descargar_hoja,
            width=200,
            height=30,
            show=False,
            tag="descargar_hoja",
        )
        dpg.add_image(
            "textura_plantilla",
            label="plantilla",
            pos=[ANCHO_VENTANA - ANCHO_PLANTILLA, 0],
        )
        dpg.add_text(
            "Programa iniciado",
            label="Estado",
            tag="estado",
            wrap=400,
            color=(150, 150, 255, 255),
        )

    dpg.create_viewport(
        title=f"Acomodador de stickers {VERSION}", width=ANCHO_VENTANA, height=ALTO_VENTANA, x_pos=10, y_pos=10
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Ventana Primaria", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
