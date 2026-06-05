import os
import math
from typing import Literal
import cv2
import numpy as np

ACOMODAR_ANCHO = "ancho"
ACOMODAR_ALTO = "alto"
Acomodo = Literal["ancho", "alto"]
PULGADA = 25.4


def imagen_en_blanco(alto: int, ancho: int):
    img = np.ones((alto, ancho, 3), np.uint8)
    return img * 255


def mostrar_imagen(imagen: np.ndarray):
    ventana = "ventana"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(ventana, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(ventana, imagen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def cuadrar_imagen(imagen: np.ndarray):
    forma = imagen.shape
    mayor = max(forma)
    cuadrado = imagen_en_blanco(mayor, mayor)
    centro_cuadrado = int(mayor / 2)
    x0 = centro_cuadrado - int(forma[1] / 2)
    y0 = centro_cuadrado - int(forma[0] / 2)
    x1 = centro_cuadrado + forma[1] - int(forma[1] / 2)
    y1 = centro_cuadrado + forma[0] - int(forma[0] / 2)
    cuadrado[y0:y1, x0:x1] = imagen.copy()
    return cuadrado

def escalar_imagen(imagen: np.ndarray, alto: int, ancho:int):
    return cv2.resize(imagen, (ancho, alto))


class Imagen:
    def __init__(
        self, direccion: str, rellenar: float = 0.0, auto_recortar: bool = False
    ):
        if os.path.exists(direccion) and (
            direccion.endswith(".png") or direccion.endswith(".jpg")
        ):
            self.imagen = cv2.imread(direccion)
            if rellenar > 0.0:
                self.rellenar_imagen()
            elif auto_recortar:
                self.autorecortar_imagen()
            self.forma = self.imagen.shape
        else:
            self.imagen = None

    def escalar_imagen(self, escala: float) -> np.ndarray:
        return cv2.resize(self.imagen, None, fx=escala, fy=escala)

    def rellenar_imagen(self):
        return

    def autorecortar_imagen(self):
        return


class Acomodador:
    def __init__(self, alto: int, ancho: int, margenes: list[float] | None = None, dpi=300):
        self.alto = alto
        self.ancho = ancho
        self.margenes = margenes if margenes is not None else [0,0,0,0]
        self.dpi = int(dpi / PULGADA)
        if self.alto > 0 and self.ancho > 0:
            self.iniciar_plantilla()

    def iniciar_plantilla(self):
        print(f"Creando plantilla con {self.ancho}x{self.alto}mm, ")
        self.plantilla: np.ndarray = imagen_en_blanco(
            self.alto * self.dpi, self.ancho * self.dpi
        )
        y0 = int(self.margenes[0] * self.dpi)
        x0 = int(self.margenes[3] * self.dpi)
        x1 = int(self.ancho * self.dpi - self.margenes[1] * self.dpi)
        y1 = int(self.alto * self.dpi - self.margenes[2] * self.dpi)
        self.area = [
            [y0, x0],
            [y0, x1],
            [y1, x1],
            [y1, x0],
        ]
        print(f"{self.plantilla.shape[0]}x{self.plantilla.shape[1]}px")

    def mostrar_plantilla(self):
        plantilla = self.plantilla.copy()
        cv2.rectangle(
            plantilla,
            (self.area[0][1], self.area[0][0]),
            (self.area[2][1], self.area[2][0]),
            (0, 0, 0),
            5,
        )
        mostrar_imagen(plantilla)

    def acomodar_rectangular(self, imagen: Imagen, acomodo: Acomodo, cantidad: int):
        nueva_imagen, alto_total, ancho_total = self.calcular_nueva_imagen_rectangulo(
            imagen, acomodo, cantidad
        )
        nueva_forma = nueva_imagen.shape
        for j in range(math.floor(alto_total / nueva_forma[0])):
            for i in range(math.floor(ancho_total / nueva_forma[1])):
                x0 = self.area[0][1] + i * nueva_forma[1]
                y0 = self.area[0][0] + j * nueva_forma[0]
                x1 = x0 + nueva_forma[1]
                y1 = y0 + nueva_forma[0]
                self.plantilla[y0:y1, x0:x1] = nueva_imagen.copy()
                cv2.rectangle(self.plantilla, (x0, y0), (x1, y1), (0, 0, 0), 2)

    def calcular_nueva_imagen_rectangulo(
        self, imagen: Imagen, acomodo: Acomodo, cantidad: int
    ):
        ancho_total = self.area[1][1] - self.area[0][1]
        alto_total = self.area[2][0] - self.area[0][0]
        if acomodo == ACOMODAR_ANCHO:
            ancho_imagen = ancho_total / cantidad
            proporcion = ancho_imagen / imagen.forma[1]
        else:
            alto_imagen = alto_total / cantidad
            proporcion = alto_imagen / imagen.forma[0]
        return imagen.escalar_imagen(proporcion), alto_total, ancho_total

    def calcular_nueva_imagen_circulo(
        self, imagen: Imagen, acomodo: Acomodo, cantidad: int
    ):
        ancho_total = self.area[1][1] - self.area[0][1]
        alto_total = self.area[2][0] - self.area[0][0]
        if acomodo == ACOMODAR_ANCHO:
            ancho_imagen = ancho_total / (cantidad + 0.5)
            proporcion = ancho_imagen / imagen.forma[1]
        else:
            alto_imagen = alto_total / (cantidad + 0.5)
            proporcion = alto_imagen / imagen.forma[0]
        nueva = imagen.escalar_imagen(proporcion)
        return cuadrar_imagen(nueva), alto_total, ancho_total

    def acomodar_circular(self, imagen: Imagen, acomodo: Acomodo, cantidad: int):
        nueva_imagen, alto_total, ancho_total = self.calcular_nueva_imagen_circulo(
            imagen, acomodo, cantidad
        )
        nueva_forma = nueva_imagen.shape
        print(nueva_forma)
        radio = int(nueva_forma[0] / 2)  # Suponiendo que la imagen es simétrica
        distancia = int(radio * math.sqrt(3))
        if acomodo == ACOMODAR_ANCHO:
            coordenadas = []
            for j in range(math.floor(alto_total / distancia)):
                for i in range(cantidad):
                    if j % 2 == 0:
                        x0 = self.area[0][1] + i * nueva_forma[1]
                        y0 = self.area[0][0] + j * distancia
                    else:
                        x0 = self.area[0][1] + radio + i * nueva_forma[1]
                        y0 = self.area[0][0] + j * distancia
                    x1 = x0 + nueva_forma[1]
                    y1 = y0 + nueva_forma[0]
                    coordenadas.append([y0, y1, x0, x1])
        else:
            coordenadas = []
            for i in range(math.floor(ancho_total / distancia)):
                for j in range(cantidad):
                    if i % 2 == 0:
                        x0 = self.area[0][1] + i * distancia
                        y0 = self.area[0][0] + j * nueva_forma[0]
                    else:
                        x0 = self.area[0][1] + i * distancia
                        y0 = self.area[0][0] + radio + j * nueva_forma[0]
                    x1 = x0 + nueva_forma[1]
                    y1 = y0 + nueva_forma[0]
                    coordenadas.append([y0, y1, x0, x1])
        for coord in coordenadas:
            self.plantilla[coord[0] : coord[1], coord[2] : coord[3]] = np.bitwise_and(
                nueva_imagen.copy(),
                self.plantilla[coord[0] : coord[1], coord[2] : coord[3]],
            )
        for coord in coordenadas:
            cv2.circle(
                self.plantilla,
                (int((coord[3] + coord[2]) / 2), int((coord[1] + coord[0]) / 2)),
                radio,
                (0, 0, 0),
                2,
            )
