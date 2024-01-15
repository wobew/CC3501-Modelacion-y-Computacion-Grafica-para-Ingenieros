from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import pyglet
import os.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.gpu_shape as gs
from grafica.obj_handler import read_OBJ
from grafica.assets_path import getAssetPath
import grafica.shaders as sh
from OpenGL.GL import *


WIDTH, HEIGHT = 800, 800
ASSETS = {
    "nave_obj": getAssetPath("nave.obj"),
    "rubik_obj": getAssetPath("rubik.obj"),
    "pochita_obj": getAssetPath("pochita.obj"),
    "hongo_obj": getAssetPath("hongo.obj"),
    "shine_obj": getAssetPath("shine.obj"),
    "yellowcube_obj": getAssetPath("yellowcube.obj")
}


# la clase objeto recibe como parámetros el pipeline, las coordenadas en rgb del color 
# y un string que hace referencia al tipo de objeto que se quiere crear
class Objeto:
    def __init__(self, pipeline, r, g, b, tipo):
        self.obj_color = (r,g,b)
        self.pipeline = pipeline
        if tipo == "cubo":
            self.shape = gs.createGPUShape(self.pipeline,
                                        read_OBJ(ASSETS["rubik_obj"], self.obj_color))
        elif tipo == "pochita":
            self.shape = gs.createGPUShape(self.pipeline,
                                        read_OBJ(ASSETS["pochita_obj"], self.obj_color))
        elif tipo == "hongo":
            self.shape = gs.createGPUShape(self.pipeline,
                                        read_OBJ(ASSETS["hongo_obj"], self.obj_color))
        elif tipo == "shine":
            self.shape = gs.createGPUShape(self.pipeline,
                                        read_OBJ(ASSETS["shine_obj"], self.obj_color))
        elif tipo == "yellowcube":
            self.shape = gs.createGPUShape(self.pipeline,
                                        read_OBJ(ASSETS["yellowcube_obj"], self.obj_color))
                 
        self.node = sg.SceneGraphNode("objeto")
        self.node.childs += [self.shape]


# definimos las clases de nave y sombra de manera análoga, solo cambiando el color
class Nave:
    def __init__(self, pipeline, x, y, z):
        self.pipeline = pipeline
        self.shape = gs.createGPUShape(self.pipeline,
                                       read_OBJ(ASSETS["nave_obj"], (0.7, 0.2, 0.6)))
        
        self.node = sg.SceneGraphNode("nave")
        self.node.transform = tr.matmul([tr.translate(x, y, z)])
        self.node.childs += [self.shape]
        
class Sombra:
    def __init__(self, pipeline, x, y, z):
        self.pipeline = pipeline
        self.shape = gs.createGPUShape(self.pipeline,
                                       read_OBJ(ASSETS["nave_obj"], (0,0,0)))
        self.node = sg.SceneGraphNode("sombra")
        self.node.transform = tr.matmul([tr.translate(x, y, z)])
        self.node.childs += [self.shape]


# definimos las clases escuadrón y escuadrón sombra también de manera análoga, estas agrupan tres instancias de naves y sombras
# ordenadas en formación de escuadrón respectivamente, se detalla a continuación
class Escuadron:
    def __init__(self, pipeline):
        self.lider = Nave(pipeline, 0, 0, 0)
        self.izquierda = Nave(pipeline, -3, -3, 0)
        self.derecha = Nave(pipeline, 3, -3, 0)
        self.node = sg.SceneGraphNode("escuadron")
        self.node.childs += [self.lider.node, self.izquierda.node, self.derecha.node]
        
        # parámetros a utilizar para definir el movimiento, cambian de valor con el input del usuario
        self.advance = 0
        self.subir = 0
        self.theta = 0
        self.phi = 0
        self.roty = 0
        self.rotz = 0
        self.posX = 0
        self.posY = 0
        self.posZ = 0

    def update(self):
        self.phi += self.roty /10
        self.theta += self.rotz /10

        # la transformación de coordenadas esféricas quedó rara porque no me di cuenta que mi uso de los ejes cartesianos no coincide
        # con el estándar de OpenGL, aún así es completamente funcional y el profesor me dijo que estaba bien mientras funcionase.
        # a veces puede parecer que el movimiento de la rotación inputada por el mouse se invierte, pero no es así porque esto solo ocurre
        # cuando la nave está de cabeza, es decir, se mueve bien en todo momento, solo que como la nave no tiene texturas es difícil ver cuándo 
        # está de cabeza,,, ojito
        self.posX += np.sin(self.phi) * np.sin(self.theta - np.pi/2) * self.advance / 10
        self.posY += np.cos(self.phi) * np.sin(self.theta + np.pi/2) * self.advance / 10
        self.posZ += np.sin(self.theta) * self.advance / 10
        self.node.transform = tr.matmul([tr.translate(self.posX, self.posY, self.posZ),
                                        tr.rotationZ(self.phi), tr.rotationX(self.theta),
                                        tr.uniformScale(0.5)])

class EscuadronSombra:
    def __init__(self, pipeline):
        self.slider = Sombra(pipeline, 0, 0, 0)
        self.sizquierda = Sombra(pipeline, -3, -3, 0)
        self.sderecha = Sombra(pipeline, 3, -3, 0)
        self.node = sg.SceneGraphNode("escuadrons")
        self.node.childs += [self.slider.node, self.sizquierda.node, self.sderecha.node]
        
        self.advance = 0
        self.subir = 0
        self.theta = 0
        self.phi = 0
        self.roty = 0
        self.rotz = 0
        self.posX = 0
        self.posY = 0
        self.posZ = 0

    def update(self):
        self.phi += self.roty /10
        self.theta += self.rotz /10

        self.posX += np.sin(self.phi) * np.sin(self.theta - np.pi/2) * self.advance / 10
        self.posY += np.cos(self.phi) * np.sin(self.theta + np.pi/2) * self.advance / 10
        self.posZ += np.sin(self.theta) * self.advance / 10

        # las únicas diferencias en el movimiento son que el escuadrón de sombras es aplastado y fijado a altura aproximada del suelo 
        # (para que se vea bien y no genere errores gráficos al chocar con este último)
        self.node.transform = tr.matmul([tr.translate(self.posX, self.posY, -1.5),
                                         tr.scale(1,1,0.1),
                                         tr.rotationZ(self.phi), tr.rotationX(self.theta),
                                         tr.uniformScale(0.5)])
        
        # pude haber puesto un límite al movimiento del escuadrón de naves para que no atraviesen las sombras y el suelo
        # (las naves pueden ir bajo el suelo y las sombras se proyectarán encima de estas por la superficie del suelo!!), 
        # pero sería simplemente agregar una condición "if" que restringiría la libertad de movimiento de la nave, prefiero
        # verlo en manera más detallada y desarrollarlo mejor en la siguiente tarea cuando tengamos que implementar 
        # interacciones entre objetos (en este caso, entre el escuadron de naves, sus sombras y el suelo)

# Controller construido sobre la base del aux 5 que contiene el grafo de escena       
class Controller(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.total_time = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()

        self.obj_color = (0.7, 0.2, 0.6)
        self.ex_shape = gs.createGPUShape(self.pipeline,
                                       read_OBJ(ASSETS["nave_obj"], self.obj_color))

        self.scene = sg.SceneGraphNode("scene")

        # los objetos en general están dispuestos a lo largo de la dirección "y", es decir, se debe avanzar en línea recta por 
        # la pista para poder verlos, el profesor dijo en el foro que se pueden repetir instancias de un objeto para cumplir con los 5...
        # yo repetí un cubo con distinto color, tamaño, orientación y posición
        self.objeto_class = Objeto(self.pipeline, 0.1, 0.8, 0.32, "cubo")
        self.objeto_node = self.objeto_class.node
        self.objeto_node.transform = tr.matmul([tr.translate(2, 25, 5), tr.uniformScale(30), tr.rotationZ(30), tr.rotationX(30)])
        self.scene.childs += [self.objeto_node]

        self.objeto_class = Objeto(self.pipeline, 0.5, 0.6, 0.7, "cubo")
        self.objeto_node = self.objeto_class.node
        self.objeto_node.transform = tr.matmul([tr.translate(4,10.3,-0.35), tr.uniformScale(40)])
        self.scene.childs += [self.objeto_node]

        self.objeto_class = Objeto(self.pipeline, 0.85, 0.33, 0.22, "pochita")
        self.objeto_node = self.objeto_class.node
        self.objeto_node.transform = tr.matmul([tr.translate(-4,20,-2),tr.rotationZ(40), tr.rotationX(-30),
                                                tr.rotationY(5), tr.uniformScale(5)])
        self.scene.childs += [self.objeto_node]

        self.objeto_class = Objeto(self.pipeline, 0.87, 0.14, 0.14, "hongo")
        self.objeto_node = self.objeto_class.node
        self.objeto_node.transform = tr.matmul([tr.translate(0.6,55,2),tr.rotationX(-30),tr.uniformScale(0.07)])
        self.scene.childs += [self.objeto_node]

        self.objeto_class = Objeto(self.pipeline, 0.76, 0.8, 0.1, "shine")
        self.objeto_node = self.objeto_class.node
        self.objeto_node.transform = tr.matmul([tr.translate(0,60,10),tr.rotationX(-30),tr.uniformScale(5)])
        self.scene.childs += [self.objeto_node]

        self.objeto_class = Objeto(self.pipeline, 0.6, 0.6, 0.6, "yellowcube")
        self.objeto_node = self.objeto_class.node
        self.objeto_node.transform = tr.matmul([tr.translate(0,-100,-2), tr.scale(0.5, 1000, 0.0001)])
        self.scene.childs += [self.objeto_node]

        self.escuadron = Escuadron(self.pipeline)
        self.escuadron_node = self.escuadron.node
        self.scene.childs += [self.escuadron_node]

        self.escuadronsombra = EscuadronSombra(self.pipeline)
        self.escuadronsombra_node = self.escuadronsombra.node
        self.scene.childs += [self.escuadronsombra_node]

class Camera:
    def __init__(self):
        # se inicializa y mira hacia (0, 0, 0) ??????!!!!
        self.at = np.array([0,0,0])
        self.eye = np.array([0, 0, 0])
        self.up = np.array([0,0,1])
        self.projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

    def update(self):
        # la cámara se actualiza para seguir al escuadrón de naves y mantenerse a una distancia y dirección constante con respecto
        # a este, por eso es irrelevante inicializar la cámara en y mirando hacia (0, 0, 0)
        self.at = np.array([controller.escuadron.posX, controller.escuadron.posY, controller.escuadron.posZ])
        self.eye = self.at + np.array([20, -20, 10])
    
camera = Camera()
controller = Controller(width=WIDTH, height=HEIGHT)
glClearColor(0, 0, 0, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(controller.pipeline.shaderProgram)

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.W:
        controller.escuadron.advance = 1
        controller.escuadronsombra.advance = 1
    if symbol == pyglet.window.key.S:
        controller.escuadron.advance = -1
        controller.escuadronsombra.advance = -1
    if symbol == pyglet.window.key.A:
        controller.escuadron.roty = 1
        controller.escuadronsombra.roty = 1
    if symbol == pyglet.window.key.D:
        controller.escuadron.roty = -1
        controller.escuadronsombra.roty = -1

@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.W:
        controller.escuadron.advance = 0
        controller.escuadronsombra.advance = 0
    if symbol == pyglet.window.key.S:
        controller.escuadron.advance = 0
        controller.escuadronsombra.advance = 0
    if symbol == pyglet.window.key.A:
        controller.escuadron.roty = 0
        controller.escuadronsombra.roty = 0
    if symbol == pyglet.window.key.D:
        controller.escuadron.roty = 0
        controller.escuadronsombra.roty = 0

@controller.event
def on_mouse_motion(x, y, dx, dy):
    if dy > 0:
        controller.escuadron.rotz = 1.5
        controller.escuadronsombra.rotz = 1.5
    elif dy < 0:
        controller.escuadron.rotz = -1.5
        controller.escuadronsombra.rotz = -1.5
    

@controller.event
def on_draw():
    controller.clear()
    controller.escuadron.update()
    controller.escuadronsombra.update()
    controller.escuadron.rotz = 0
    controller.escuadronsombra.rotz = 0

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camera.update()
    view = tr.lookAt(
        camera.eye,
        camera.at,
        camera.up
    )
    
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    sg.drawSceneGraphNode(controller.scene, controller.pipeline, "model")

def update(dt, controller):
    controller.total_time += dt

if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
