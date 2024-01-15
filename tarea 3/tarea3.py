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
import os
from itertools import chain
from pathlib import Path
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Vec2
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
)
import math as mt

WIDTH, HEIGHT = 800, 800
ASSETS = {
    "nave_obj": getAssetPath("nave.obj"),
    "rubik_obj": getAssetPath("rubik.obj"),
    "pochita_obj": getAssetPath("pochita.obj"),
    "hongo_obj": getAssetPath("hongo.obj"),
    "shine_obj": getAssetPath("shine.obj"),
    "yellowcube_obj": getAssetPath("yellowcube.obj")
}

half_width = WIDTH // 2
half_height = HEIGHT // 2

HermiteCurveFinal, tangentes = [], []
step, enes, largo, theta= 0, 0, 0, 0
N = 10

with open(Path(os.path.dirname(__file__)) / "point_vertex_program.glsl") as f:
        vertex_program = f.read()
with open(Path(os.path.dirname(__file__)) / "point_fragment_program.glsl") as f:
        fragment_program = f.read()

vert_shader = Shader(vertex_program, "vertex")
frag_shader = Shader(fragment_program, "fragment")
pipeline2 = ShaderProgram(vert_shader, frag_shader)

projection2 = tr.ortho(
        -half_width, half_width, -half_height, half_height, 0.001, 10.0
    )

view2 = tr.lookAt(
        np.array([half_width, half_height, 1.0]),  # posición de la cámara
        np.array([half_width, half_height, 0.0]),  # hacia dónde apunta
        np.array([0.0, 1.0, 0.0]),  # vector para orientarla (arriba)
    )

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

class Escuadron:
    def __init__(self, pipeline):
        self.lider = Nave(pipeline, 0, 0, 0)
        self.izquierda = Nave(pipeline, -3, -3, 0)
        self.derecha = Nave(pipeline, 3, -3, 0)
        self.node = sg.SceneGraphNode("escuadron")
        self.node.childs += [self.lider.node, self.izquierda.node, self.derecha.node]
        
        self.advance = 0
        self.subir = 0
        self.theta = 0
        self.phi = 0
        self.roty = 0
        self.rotz = 0
        self.posX = 0
        self.posY = 0
        self.posZ = 0
        self.posiciones = []
        self.orientaciones = []
        self.angulos = []
        self.pirueta = False
        self.graficar = False
        self.theta0 = 0
        self.repro = False

    def update(self):
        self.phi += self.roty / 15
        self.theta += self.rotz / 15
        

        if not self.pirueta:
            self.posX += np.sin(self.phi) * np.sin(self.theta - np.pi/2) * self.advance / 10
            self.posY += np.cos(self.phi) * np.sin(self.theta + np.pi/2) * self.advance / 10
            self.posZ += np.sin(self.theta) * self.advance / 10
        
        # BONUS 2 - al presionar la tecla P se entra en modo pirueta:
        # se guarda el valor inicial de theta en theta0, luego se aumenta theta en controller update hasta completar un giro de 360 grados
        # se omite el uso de advance y se duplica la velocidad para que la nave realice una vuelta rápida y pronunciada sobre sí misma
        else:
            self.posX += np.sin(self.phi) * np.sin(self.theta - np.pi/2) / 5
            self.posY += np.cos(self.phi) * np.sin(self.theta + np.pi/2) / 5
            self.posZ += np.sin(self.theta) / 5

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
        
    def update(self):
            self.node.transform = tr.matmul([tr.translate(controller.escuadron.posX, controller.escuadron.posY, -1.5),
                                            tr.scale(1,1,0.1),
                                            tr.rotationZ(controller.escuadron.phi), tr.rotationX(controller.escuadron.theta),
                                            tr.uniformScale(0.5)])
        
class Controller(pyglet.window.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.total_time = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()
        self.node_data = []
        self.joint_data = []

        self.obj_color = (0.7, 0.2, 0.6)
        self.ex_shape = gs.createGPUShape(self.pipeline,
                                       read_OBJ(ASSETS["nave_obj"], self.obj_color))

        self.scene = sg.SceneGraphNode("scene")

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
        self.proyecciones = False

    def update(self):
        self.at = np.array([controller.escuadron.posX, controller.escuadron.posY, controller.escuadron.posZ])


        if not self.proyecciones:
            self.projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)
            self.eye = self.at + np.array([20, -20, 10])
            self.up = np.array([0,0,1])
            
        
        else:
            # BONUS 1 - al apretar C se cambia a una vista tipo tercera persona, donde la camara basicamente actua como una cuarta nave del escuadron
            # ubicada siempre detras del resto, se corrige el vector "Up" para el caso en que la nave este mirando hacia abajo
            self.projection = tr.perspective(60, float(WIDTH)/float(HEIGHT), 0.1, 100)
            
            self.eye = self.at - np.array([ 4.5*np.sin(controller.escuadron.phi) * np.sin(controller.escuadron.theta - np.pi/2),
                                                4.5*np.cos(controller.escuadron.phi) * np.sin(controller.escuadron.theta + np.pi/2),
                                                4.5*np.sin(controller.escuadron.theta) ])
            if np.cos(controller.escuadron.theta) > 0:
                self.up = np.array([0,0,1]) 
            else:
                self.up = np.array([0,0,-1])
                                            
            
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def hermiteMatrix(P1, P2, T1, T2):
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])
    return np.matmul(G, Mh)

def evalCurve(M, N):
    ts = np.linspace(0.0, 1.0, N)
    curve = np.ndarray(shape=(N, 3), dtype=float)
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
    return curve

camera = Camera()
controller = Controller(width=WIDTH, height=HEIGHT)
glClearColor(0, 0, 0, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(controller.pipeline.shaderProgram)

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.W:
        controller.escuadron.advance = 1
    if symbol == pyglet.window.key.S:
        controller.escuadron.advance = -1
    if not controller.escuadron.pirueta:
        if symbol == pyglet.window.key.A:
            controller.escuadron.roty = 1
        if symbol == pyglet.window.key.D:
            controller.escuadron.roty = -1
    if symbol == pyglet.window.key.P:
        global theta
        if not controller.escuadron.repro:
            controller.escuadron.pirueta = True
            controller.escuadron.theta0 = controller.escuadron.theta
    if symbol == pyglet.window.key.V:
        controller.escuadron.graficar = not controller.escuadron.graficar
    if symbol == pyglet.window.key.R:
        global HermiteCurveFinal
        global largo
        global N
        global enes

        # hay una distancia mínima de 3.5 entre cada punto de control con el último registrado para evitar que se superpongan
        # y que se genere un movimiento brusco
        if not(len(controller.escuadron.posiciones) == 0):
            if np.linalg.norm(np.array([controller.escuadron.posiciones[-1]]).T -  
                            np.array([[controller.escuadron.posX, controller.escuadron.posY, controller.escuadron.posZ]]).T) < 3.5:
                return

        controller.escuadron.posiciones.append([controller.escuadron.posX, controller.escuadron.posY, controller.escuadron.posZ])
        controller.escuadron.orientaciones.append([np.sin(controller.escuadron.phi) * np.sin(controller.escuadron.theta - np.pi/2)*6, 
                                                   np.cos(controller.escuadron.phi) * np.sin(controller.escuadron.theta + np.pi/2)*6,
                                                   np.sin(controller.escuadron.theta)*6])
        controller.escuadron.angulos.append([controller.escuadron.theta, controller.escuadron.phi])

        largo = len(controller.escuadron.posiciones) - 1
        if largo == 0:
            return
        i = 0
        while i < largo:
            P1, P2 = np.array([controller.escuadron.posiciones[i]]).T, np.array([controller.escuadron.posiciones[i+1]]).T
            T1, T2 = np.array([controller.escuadron.orientaciones[i]]).T, np.array([controller.escuadron.orientaciones[i+1]]).T
            dist = np.linalg.norm(P2 - P1)
            N1 = int(dist * N)
            if i == 0:
                GMh = hermiteMatrix(P1, P2, T1, T2)
                HermiteCurve = evalCurve(GMh, N1)
                if largo == 1:
                    HermiteCurveFinal = HermiteCurve
            else:
                GMh = hermiteMatrix(P1, P2, T1, T2)
                HermiteCurve1 = evalCurve(GMh, N1)
                if i == 1:
                    HermiteCurve = HermiteCurve[:-1]
                    HermiteCurveFinal = np.concatenate((HermiteCurve, HermiteCurve1), axis=0)
                else:
                    HermiteCurveFinal = HermiteCurveFinal[:-1]
                    HermiteCurveFinal = np.concatenate((HermiteCurveFinal, HermiteCurve1), axis=0)
            i += 1
        enes , y = HermiteCurveFinal.shape

    if symbol == pyglet.window.key.C:
        camera.proyecciones = not camera.proyecciones

    if symbol == pyglet.window.key._1:
        global tangentes
        if len(HermiteCurveFinal) > 1:
            controller.escuadron.repro = not controller.escuadron.repro
            for i in range(0, len(HermiteCurveFinal)):
                if i == len(HermiteCurveFinal) - 1:
                    tangentes += [[HermiteCurveFinal[i-1][0] - HermiteCurveFinal[i][0],
                            HermiteCurveFinal[i-1][1] - HermiteCurveFinal[i][1],
                            HermiteCurveFinal[i-1][2] - HermiteCurveFinal[i][2]]]
                    break
                tangentes += [[HermiteCurveFinal[i][0] - HermiteCurveFinal[i+1][0],
                            HermiteCurveFinal[i][1] - HermiteCurveFinal[i+1][1],
                            HermiteCurveFinal[i][2] - HermiteCurveFinal[i+1][2]]]
            controller.escuadron.posiciones = []
            controller.escuadron.orientaciones = []
            controller.escuadron.angulos = []
            
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.W:
        controller.escuadron.advance = 0
    if symbol == pyglet.window.key.S:
        controller.escuadron.advance = 0
    if not controller.escuadron.pirueta:
        if symbol == pyglet.window.key.A:
            controller.escuadron.roty = 0
        if symbol == pyglet.window.key.D:
            controller.escuadron.roty = 0

@controller.event
def on_mouse_motion(x, y, dx, dy):
    if not controller.escuadron.pirueta:
        if dy > 0:
            controller.escuadron.rotz = 1.5
        elif dy < 0:
            controller.escuadron.rotz = -1.5
    
@controller.event
def on_draw():
    global HermiteCurveFinal, N, step
    global largo, enes, pipeline2, tangentes
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
    
    if controller.escuadron.graficar:
        if len(HermiteCurveFinal) > 0:    
            node_data = pipeline2.vertex_list(len(HermiteCurveFinal), pyglet.gl.GL_POINTS, position="f")
            joint_data = pipeline2.vertex_list_indexed(len(HermiteCurveFinal), pyglet.gl.GL_LINES,
                                                        tuple(chain(*(j for j in [range(len(HermiteCurveFinal))]))), position="f",)
            node_data.position[:] = tuple(chain(*((p[0], p[1], p[2]) for p in HermiteCurveFinal)))
            joint_data.position[:] = tuple(chain(*((p[0], p[1], p[2]) for p in HermiteCurveFinal)))

            pipeline2.use()
            pipeline2["projection"] = camera.projection.reshape(16, 1, order="F")
            pipeline2["view"] = view.reshape(16, 1, order="F")
            node_data.draw(pyglet.gl.GL_POINTS)
            node_data.draw(pyglet.gl.GL_LINES)
            glUseProgram(controller.pipeline.shaderProgram)

    if controller.escuadron.repro:
        if step >= enes - 1:
            step = 0
            controller.escuadron.repro = False
            HermiteCurveFinal = []
            enes = 0
            return
        controller.escuadron.posX = HermiteCurveFinal[step][0]
        controller.escuadron.posY = HermiteCurveFinal[step][1]
        controller.escuadron.posZ = HermiteCurveFinal[step][2]
        #controller.escuadron.phi = mt.atan2(tangentes[step][0], tangentes[step][1])
        #controller.escuadron.phi = mt.atan2(mt.sqrt(tangentes[step][0]**2 + tangentes[step][1]**2), tangentes[step][2])
        step += 1
        
def update(dt, controller):
    controller.total_time += dt
    if controller.escuadron.pirueta:   
            controller.escuadron.theta += 7*dt
            if controller.escuadron.theta >= 2*np.pi + controller.escuadron.theta0:
                controller.escuadron.pirueta = False

if __name__ == '__main__':
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
