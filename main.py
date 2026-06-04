import cv2
from src.acomodador_de_stickers.acomodador import Acomodador, Imagen, mostrar_imagen
from src.acomodador_de_stickers.interfaz import crear_interfaz

def main():
    acomodador = Acomodador(10, 8, [0.5, 0.5, 0.5, 0.5])
    #acomodador.mostrar_plantilla()
    # imagen = Imagen("imagen_de_prueba.png")
    #acomodador.acomodar_rectangular(imagen, "alto", 3)
    # acomodador.acomodar_circular(imagen, "ancho", 5)
    # acomodador.mostrar_plantilla()
    crear_interfaz()



if __name__ == "__main__":
    main()
