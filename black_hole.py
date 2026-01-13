import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
from jets import generate_jet_particles
from tde import TDE
from accretion_disk import AccretionDisk


class BlackHoleScene(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle("TDE Visualization")
        self.setGeometry(100, 100, 800, 600)

        # rotation
        self.angle = 0.2

        # camera
        self.cam_distance = 120.0
        self.cam_angle_x = 20.0
        self.cam_angle_y = 0.0
        self.last_mouse_pos = None

        # stars
        self.num_stars = 10000
        self.star_positions = self.generate_stars(self.num_stars, 400)
        self.star_colors, self.star_sizes, self.star_flicker_phase = self.generate_star_visuals(
            self.num_stars)
        self.star_frequencies = np.random.uniform(0.5, 3.0, self.num_stars)

        # jets
        self.jet_particles_base = generate_jet_particles(
            color_profile='white_blue_to_red')
        self.jet_particles = self.jet_particles_base.copy()
        self.flashes = np.random.uniform(0.0, 0.3, len(self.jet_particles))
        self.jet_velocity_z = np.zeros(len(self.jet_particles))
        self.jet_color_progress = 0.0  # 0 = base color, 1 = full change after TDE
        self.jet_color_speed = 0.02  # color change speed per frame
        # Wobble settings (adjustable)
        self.wobble_amplitude = 2.0  # amplitude (higher = stronger wobble)
        self.wobble_frequency = 2.0  # frequency (higher = faster wobble)
        self.wobble_delay_frames = 30  # delay frames after TDE start
        self.tde_frame_counter = 0  # frame counter for delay
        # thickness multiplier (1.0 = no change, 2.0 = double)
        self.jet_thickness_multiplier = 1.5

        # TDE
        self.tde = TDE(bh_position=np.zeros(3), M_bh=10.0)

        # disk
        self.accretion_disk = AccretionDisk()

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)

    # ---------------------------------------
    # stars GENERATION
    # ---------------------------------------
    def generate_stars(self, n, radius):
        phi = np.random.uniform(0, 2*np.pi, n)
        costheta = np.random.uniform(-1, 1, n)
        u = np.random.uniform(0, 1, n)
        theta = np.arccos(costheta)
        r = radius * np.cbrt(u)
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return np.column_stack((x, y, z))

    # ---------------------------------------
    # stars CONTROL
    # ---------------------------------------
    def generate_star_visuals(self, n):
        temps = np.random.uniform(2500, 12000, n)

        def bb_to_rgb(T):
            t = T/10000
            r = np.clip(1.5*t, 0, 1)
            b = np.clip(1.8*(1-t), 0, 1)
            g = (r+b)*0.55
            return r, g, b
        colors = np.array([bb_to_rgb(T) for T in temps], dtype=float)
        sizes = np.where(np.random.rand(n) < 0.03, np.random.uniform(
            2.6, 3.6, n), np.random.uniform(1.2, 2.0, n))
        phases = np.random.uniform(0, 2*np.pi, n)
        return colors, sizes, phases

    # ---------------------------------------
    # OpenGL init
    # ---------------------------------------
    def initializeGL(self):
        glClearColor(0.02, 0.02, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_COLOR_MATERIAL)
        self.bh_quad = gluNewQuadric()
        self.rim_quad = gluNewQuadric()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w/h if h != 0 else 1, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    # ----------------------------------------
    # JETS
    # ----------------------------------------
    def draw_jets(self):
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # Group particles by size for batch rendering
        unique_sizes = np.unique(self.jet_particles[:, 6])
        for size in unique_sizes:
            idxs = np.where(self.jet_particles[:, 6] == size)[0]
            if len(idxs) == 0:
                continue
            pos = self.jet_particles[idxs, :3].astype(np.float32)
            col = np.column_stack((self.jet_particles[idxs, 3:6], np.full(
                len(idxs), 0.45))).astype(np.float32)

            glPointSize(float(size))
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, pos)
            glColorPointer(4, GL_FLOAT, 0, col)
            glDrawArrays(GL_POINTS, 0, len(idxs))
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

        glDisable(GL_BLEND)
        glPopMatrix()

    # ---------------------------------------
    # STARS & twinkling
    # ---------------------------------------
    def draw_stars(self):
        glPushMatrix()
        t = self.angle * 200.0
        # Vectorized twinkling
        flicker_factors = 0.85 + 0.15 * \
            np.sin(t * self.star_frequencies + self.star_flicker_phase)
        colors_adjusted = (self.star_colors.T *
                           flicker_factors).T.astype(np.float32)
        # Group by size
        size_bins = np.array([1.2, 1.6, 2.0, 2.8, 3.6])
        bin_idx = np.digitize(self.star_sizes, size_bins, right=True)
        for b in np.unique(bin_idx):
            idxs = np.where(bin_idx == b)[0]
            if len(idxs) == 0:
                continue
            pos_bin = self.star_positions[idxs].astype(np.float32)
            col_bin = colors_adjusted[idxs].astype(np.float32)
            glPointSize(float(np.median(self.star_sizes[idxs])))
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, pos_bin)
            glColorPointer(3, GL_FLOAT, 0, col_bin)
            glDrawArrays(GL_POINTS, 0, len(idxs))
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)
        glPopMatrix()

    # ---------------------------------------
    # BLACK HOLE
    # ---------------------------------------
    def draw_black_hole(self):
        glPushMatrix()
        glColor3f(0, 0, 0)
        gluSphere(self.bh_quad, self.accretion_disk.inner_radius, 50, 50)
        glPopMatrix()

    # ---------------------------------------
    # RIM GLOW
    # ---------------------------------------
    def draw_rim_glow(self):
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glColor4f(1.0, 0.8, 0.5, 0.18)
        gluSphere(self.rim_quad, self.accretion_disk.inner_radius + 1.1, 50, 50)
        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glPopMatrix()

    # ---------------------------------------
    # TDE
    # ---------------------------------------
    def draw_tde(self):
        if self.tde.active and self.tde.particles is not None:
            glPushMatrix()
            glRotatef(140, 1, 0, 0)
            glRotatef(15, 1, 0, 0)
            glRotatef(-15, 0, 1, 0)
            glPointSize(3.0)

            t = self.angle * 200.0
            # Vectorized flickering
            flick = 0.85 + 0.15 * np.sin(t + self.tde.flicker_phases)
            colors_adjusted = (self.tde.colors.T * flick).T.astype(np.float32)
            pos = self.tde.particles.astype(np.float32)

            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, pos)
            glColorPointer(3, GL_FLOAT, 0, colors_adjusted)
            glDrawArrays(GL_POINTS, 0, len(pos))
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

            glPopMatrix()

    # ---------------------------------------
    # PAINT GL
    # ---------------------------------------
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # camera
        glTranslatef(0, 0, -self.cam_distance)
        glRotatef(-self.cam_angle_x, 1, 0, 0)
        glRotatef(-self.cam_angle_y, 0, 1, 0)

        self.draw_stars()
        self.draw_black_hole()
        self.draw_rim_glow()
        self.draw_tde()
        self.accretion_disk.draw()

        # jets
        glPushMatrix()
        glRotatef(-20, 1, 0, 0)
        self.draw_jets()
        glPopMatrix()

    # ---------------------------------------
    # ANIMATION
    # ---------------------------------------
    def update_scene(self):
        self.angle += 0.0004
        self.accretion_disk.update()
        self.tde.update(dt=4)

        if self.tde.active and self.tde.disrupted and self.tde.moving:
            self.tde_frame_counter += 1
            self.jet_velocity_z = np.zeros(len(self.jet_particles))
            self.jet_color_progress = min(
                self.jet_color_progress + self.jet_color_speed, 1.0)
            self.update_jets_for_tde(progress=self.jet_color_progress)
        else:
            self.jet_velocity_z = np.zeros(len(self.jet_particles))
            self.tde_frame_counter = 0
            if self.jet_color_progress > 0:
                self.jet_color_progress = max(
                    self.jet_color_progress - self.jet_color_speed, 0.0)
                self.update_jets_for_tde(progress=self.jet_color_progress)
            if not self.tde.moving and np.any(self.jet_particles != self.jet_particles_base):
                alpha = 0.1
                self.jet_particles = (
                    1 - alpha) * self.jet_particles + alpha * self.jet_particles_base
                self.jet_velocity_z = (
                    1 - alpha) * self.jet_velocity_z + alpha * np.zeros(len(self.jet_velocity_z))
                self.flashes = np.random.uniform(
                    0.0, 0.3, len(self.jet_particles))
        self.jet_particles[:, 2] += self.jet_velocity_z
        self.update()

    # ---------------------------------------
    # JETS AFTER TDE
    # ---------------------------------------
    def update_jets_for_tde(self, progress=1.0):
        if not self.tde.moving:
            self.jet_particles[:, :3] = self.jet_particles_base[:, :3].copy()
            return

        self.jet_particles[:, :3] = self.jet_particles_base[:, :3].copy()

        z = self.jet_particles[:, 2]
        t = np.clip(np.abs(z) / 120.0, 0, 1)

        # Colors (gradual change after TDE via glow)
        r = np.clip(0.2 + 1.0 * t, 0, 1)
        g = np.clip(0.7 * (1 - t), 0, 1)
        b = np.clip(1.0 * (1 - t) + 0.5 * t, 0, 1)

        # Update flashes every 5 frames
        if int(self.angle * 1000) % 5 == 0:
            self.flashes = np.random.uniform(0.0, 0.3, len(self.jet_particles))
        r += self.flashes * 0.5
        b += self.flashes * 0.3

        # Glow with gradual brightness increase via progress
        r_glow = np.clip(r * 1.2, 0, 1)
        g_glow = np.clip(g * 1.2, 0, 1)
        b_glow = np.clip(b * 1.2, 0, 1)

        # Blend with base color + glow
        self.jet_particles[:, 3] = (
            1 - progress) * self.jet_particles_base[:, 3] + progress * r_glow
        self.jet_particles[:, 4] = (
            1 - progress) * self.jet_particles_base[:, 4] + progress * g_glow
        self.jet_particles[:, 5] = (
            1 - progress) * self.jet_particles_base[:, 5] + progress * b_glow

        # Sizes (slight thickening via multiplier, gradual with progress)
        base_size = 4.0 * self.jet_thickness_multiplier * progress
        self.jet_particles[:, 6] = base_size * (1.0 - 0.5 * t) + 1.0

        # Simple coherent wobble (with delay)
        if self.tde_frame_counter >= self.wobble_delay_frames:
            wobble_x = self.wobble_amplitude * \
                np.sin(self.angle * self.wobble_frequency)
            wobble_y = self.wobble_amplitude * \
                np.cos(self.angle * self.wobble_frequency)
            self.jet_particles[:, 0] += wobble_x * t
            self.jet_particles[:, 1] += wobble_y * t

    # ---------------------------------------
    # CAMERA
    # ---------------------------------------

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos is None:
            return
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        self.cam_angle_y += dx * 0.5
        self.cam_angle_x += dy * 0.5
        self.cam_angle_x = np.clip(self.cam_angle_x, -90, 90)
        self.last_mouse_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.cam_distance -= delta * 5
        self.cam_distance = np.clip(self.cam_distance, 15, 400)
        self.update()

    # ---------------------------------------
    # TDE CONTROL
    # ---------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_T:
            self.tde.active = False
            self.tde.disrupted = False
            self.tde.moving = False
            self.tde.add_star(r_init=40, mass=1, radius=3)
        elif event.key() == Qt.Key_D:
            self.tde.tidal_enabled = True
            self.tde.disrupt()
