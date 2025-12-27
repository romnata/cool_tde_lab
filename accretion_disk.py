from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np


class AccretionDisk:
    def __init__(self):
        self.inner_radius = 4.0
        self.outer_radius = 15.0
        self.disk_color = (0.95, 0.45, 0.08)
        self.spiral_turns = 10
        self.spiral_samples = 900
        self.disk_normal = np.array([0.0, 0.0, 1.0])
        self.disk_angle = 0.0
        self.disk_ring_quad = gluNewQuadric()

    def update(self):
        self.disk_angle += 0.12

    def draw(self):
        glPushMatrix()
        glRotatef(140, 1, 0, 0)
        glRotatef(15, 1, 0, 0)
        glRotatef(self.disk_angle, 0, 0, 1)
        glRotatef(-15, 0, 1, 0)
        inner_r = self.inner_radius
        outer_r = self.outer_radius
        for i in range(60):
            t = i/60
            r_in = inner_r + t*(outer_r-inner_r)
            r_out = inner_r + (t+1/60)*(outer_r-inner_r)
            alpha = 0.95-0.85*t
            glColor4f(1.0, 0.45-0.25*t, 0.03+0.02*(1-t), max(0.01, alpha))
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            gluDisk(self.disk_ring_quad, r_in, r_out, 128, 1)
            glDisable(GL_BLEND)

        # spirals
        glLineWidth(1.5)
        for s_idx in range(3):
            phase = 2*np.pi/3*s_idx
            glBegin(GL_LINE_STRIP)
            for j in range(self.spiral_samples+1):
                t2 = j/self.spiral_samples
                ang = self.spiral_turns*2*np.pi*t2 + phase + self.disk_angle*0.3
                r = inner_r + t2*(outer_r-inner_r)
                x = r*np.cos(ang)
                y = r*np.sin(ang)
                z = 0.02
                s = 1.0 - t2
                glColor4f(1.0, 0.5+0.25*s, 0.2*s, 0.85*s)
                glVertex3f(x, y, z)
            glEnd()
        glPopMatrix()
