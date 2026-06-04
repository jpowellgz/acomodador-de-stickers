import math
from typing import Literal
import cv2
import numpy as np

ACOMODAR_ANCHO = "ancho"
ACOMODAR_ALTO = "alto"
Acomodo = Literal["ancho", "alto"]

def mostrar_imagen(imagen: np.ndarray):
    ventana = "ventana"
    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(ventana, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(ventana, imagen)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

class Imagen:
    def __init__(self, direccion: str, rellenar:float=0.0, auto_recortar:bool=False):
        self.imagen = cv2.imread(direccion)
        if rellenar > 0.0:
            self.rellenar_imagen()
        elif auto_recortar:
            self.autorecortar_imagen()
        self.forma = self.imagen.shape

    def escalar_imagen(self, escala: float) -> np.ndarray:
        return cv2.resize(self.imagen, None, fx=escala, fy=escala)

    def rellenar_imagen(self):
        return

    def autorecortar_imagen(self):
        return


class Acomodador:
    def __init__(self, alto: int, ancho: int, margenes: list[float], dpi=300):
        self.alto = alto
        self.ancho = ancho
        self.margenes = margenes
        self.dpi = dpi
        self.iniciar_plantilla()

    def iniciar_plantilla(self):
        self.plantilla: np.ndarray = np.ones((self.alto*self.dpi, self.ancho*self.dpi, 3), np.uint8)
        self.plantilla = self.plantilla * 255
        y0 = int(self.margenes[0]*self.dpi)
        x0 = int(self.margenes[3]*self.dpi)
        x1 = int(self.ancho*self.dpi - self.margenes[1]*self.dpi)
        y1 = int(self.alto*self.dpi -self.margenes[2]*self.dpi)
        self.area = [
            [y0, x0],
            [y0, x1],
            [y1, x1],
            [y1, x0],
        ]
    
    def mostrar_plantilla(self):
        plantilla = self.plantilla.copy()
        cv2.rectangle(plantilla, (self.area[0][1],self.area[0][0]),(self.area[3][1], self.area[3][0]),(0,0,0),5)
        mostrar_imagen(plantilla)

    def acomodar_rectangular(self, imagen: Imagen, acomodo: Acomodo, cantidad: int):
        ancho_total = self.area[1][1] - self.area[0][1]
        alto_total = self.area[2][0] - self.area[0][0]
        if acomodo == ACOMODAR_ANCHO:
            ancho_imagen = ancho_total / cantidad
            proporcion = ancho_imagen / imagen.forma[1]
        else:
            alto_imagen = alto_total / cantidad
            proporcion = alto_imagen / imagen.forma[0]
        nueva_imagen = imagen.escalar_imagen(proporcion)
        nueva_forma = nueva_imagen.shape
        cantidad_alto = math.floor(alto_total / nueva_forma[0])
        cantidad_ancho = math.floor(ancho_total / nueva_forma[1])
        print(f"cantidades Ancho:{cantidad_ancho} Alto:{cantidad_alto}")
        print(nueva_imagen.dtype, self.plantilla.dtype)
        mostrar_imagen(nueva_imagen)
        for j in range(cantidad_alto):
            for i in range(cantidad_ancho):
                x0 = self.area[0][1] + i * nueva_forma[1]
                y0 = self.area[0][0] + j * nueva_forma[0]
                x1 = self.area[0][1] + (i+1) * nueva_forma[1]
                y1 = self.area[0][0] + (j+1) * nueva_forma[0]
                print(f"Pegando en {x0},{y0}")
                self.plantilla[y0:y1, x0:x1] = nueva_imagen.copy()
                cv2.rectangle(self.plantilla,(x0,y0),(x1,y1),(0,0,0),3)


        