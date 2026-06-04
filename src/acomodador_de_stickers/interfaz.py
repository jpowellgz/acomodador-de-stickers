from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from src.acomodador_de_stickers.utils import hojas

opciones_hojas = [f"{key}: {val[0]}mm x {val[1]}mm" for key, val in hojas.items()]


@dataclass
class Opciones:
    acomodo: str
    tam_hoja: str
    margenes: list
    imagen: str

    def __init__(self):
        self.imagen = ""
        self.acomodo = "ancho"
        self.tam_hoja = "A4"
        self.margenes = [0, 0, 0, 0]


opciones = Opciones()


def callback_hoja(sender, data):
    opciones.tam_hoja = dpg.get_value(sender)[:2]


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


def callback_dir(sender, app_data):
    opciones.imagen=app_data["file_path_name"]
    print("actualizado", opciones)
    print("OK was clicked.")
    print("Sender: ", sender)
    print("App Data: ", app_data)


def cancel_callback(sender, app_data):
    print("Cancel was clicked.")
    print("Sender: ", sender)
    print("App Data: ", app_data)


def crear_interfaz():
    print(opciones)
    dpg.create_context()
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

    with dpg.window(tag="Primary Window", label="Acomodador de stickers"):
        dpg.add_button(
            label="Elegir imagen", 
            callback=lambda: dpg.show_item("archivo"),
            width=100,
            height=50,
        )
        dpg.add_text("Opciones")
        dpg.add_combo(
            tag="Hojas",
            items=opciones_hojas,
            callback=callback_hoja,
            label="Tamaño de hoja",
            width=150,
            default_value=opciones_hojas[4],
        )
        dpg.add_combo(
            tag="Acomodo",
            items=["ancho", "alto"],
            callback=callback_acomodo,
            default_value="ancho",
            label="Acomodar",
            width=150,
        )
        dpg.add_text("Márgenes (mm)")
        dpg.add_input_int(
            label="Arriba", default_value=0, width=100, callback=callback_margen_arr
        )
        dpg.add_input_int(
            label="Derecha", default_value=0, width=100, callback=callback_margen_der
        )
        dpg.add_input_int(
            label="Izquierda", default_value=0, width=100, callback=callback_margen_aba
        )
        dpg.add_input_int(
            label="Arriba", default_value=0, width=100, callback=callback_margen_izq
        )

    dpg.create_viewport(title="Custom Title", width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    while dpg.is_dearpygui_running():
        # insert here any code you would like to run in the render loop
        # you can manually stop by using stop_dearpygui()
        dpg.render_dearpygui_frame()
    dpg.destroy_context()
