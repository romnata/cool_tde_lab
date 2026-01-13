# tde.py

import numpy as np


class TDE:
    def __init__(self, bh_position, M_bh):
        # BH parameters
        self.bh_position = bh_position  # np.array([0,0,0])
        self.M_bh = M_bh
        self.G = 0.5  # Gravitational constant (simulation units)
        # Softening length to prevent singularity and infall (~ inner_radius / 2 recommended)
        self.eps = 5

        # TDE states
        self.active = False
        self.moving = False
        self.disrupted = False

        # Star and particle parameters
        self.num_particles = 90000  # Number of star particles (configurable)
        self.star_mass = None
        self.star_radius = None
        self.Rt = None
        self.star_center = None
        self.star_vel = None
        self.star_offsets = None
        self.particles_pos = None
        self.particles_vel = None
        self.particles = None  # For render compatibility
        self.colors = None  # Base particle colors
        self.flicker_phases = None  # Flicker phases (like background stars)

    def add_star(self, r_init, mass, radius, initial_angle=-2.5):
        # initial_angle: rad
        self.star_mass = mass
        self.star_radius = radius
        self.active = True
        self.moving = False
        self.disrupted = False

        # Tidal radius Rt
        self.Rt = radius * (self.M_bh / mass)**(1/3)

        # Impact parameter beta = Rt / Rp; for disruption beta >1
        beta = 5.0  # Configurable: increased to ensure disruption
        Rp = self.Rt / beta

        # Initial distance
        r = r_init

        # Parabolic orbit parameters (e=1)
        p = 2 * Rp
        cos_nu = p / r - 1
        # Add initial_angle to shift position/trajectory
        nu = np.arccos(cos_nu) + initial_angle
        sin_nu = np.sin(nu)
        cos_nu = np.cos(nu)

        # Star center position (right side for nu≈0, slightly above if initial_angle positive)
        star_x = r * cos_nu
        star_y = r * sin_nu
        star_z = 0.0  # In disk plane (xy)
        self.star_center = np.array([star_x, star_y, star_z])

        # Angular momentum L and velocities
        L = np.sqrt(self.G * self.M_bh * p)
        v_theta = L / r
        # v_r negative for approach (ccw sign)
        v_r = -(self.G * self.M_bh / L) * np.abs(sin_nu)

        # Velocity components (ccw rotation like disk; adjusted for right-side approach with left curl)
        v_x = v_r * cos_nu - v_theta * sin_nu
        v_y = v_r * sin_nu + v_theta * cos_nu
        v_z = -0.0001
        self.star_vel = np.array([v_x, v_y, v_z])

        # Generate particle offsets (uniform volume)
        self.generate_star_particles(radius)

        # Generate base colors (prior ranges)
        n = self.num_particles
        self.colors = np.empty((n, 3))
        self.colors[:, 0] = np.random.uniform(0.2, 0.5, n)
        self.colors[:, 1] = np.random.uniform(0.4, 0.6, n)
        self.colors[:, 2] = np.random.uniform(0.8, 1.0, n)

        # Flicker phases (to restore prior flickering)
        self.flicker_phases = np.random.uniform(0, 2 * np.pi, n)

        # Initial particle positions
        self.update_particles_pos()
        self.particles = self.particles_pos

    def generate_star_particles(self, radius):
        n = self.num_particles
        phi = np.random.uniform(0, 2 * np.pi, n)
        costheta = np.random.uniform(-1, 1, n)
        u = np.random.uniform(0, 1, n)
        r_dist = radius * u ** (1 / 3)  # Uniform volume
        theta = np.arccos(costheta)
        x = r_dist * np.sin(theta) * np.cos(phi)
        y = r_dist * np.sin(theta) * np.sin(phi)
        z = r_dist * np.cos(theta)
        self.star_offsets = np.column_stack((x, y, z))

    def disrupt(self):
        if self.active and not self.moving:
            self.moving = True

    def update(self, dt):
        if not self.active or not self.moving:
            return

        if not self.disrupted:
            # Update center (rigid body)
            r_vec = self.star_center - self.bh_position
            r = np.linalg.norm(r_vec)
            acc = -self.G * self.M_bh / (r**2 + self.eps**2)**1.5 * r_vec
            self.star_vel += acc * dt
            self.star_center += self.star_vel * dt

            # Check for disruption (when r < 1.5 Rt)
            if r < 1.5*self.Rt:
                self.disrupted = True
                # Switch to independent particles
                self.particles_pos = self.star_center[None,
                                                      :] + self.star_offsets
                self.particles_vel = np.tile(
                    self.star_vel, (self.num_particles, 1))
                # Add energy spread for unbound/bound fractions (~half unbound)
                ur = r_vec / r
                proj = np.einsum('ij,j->i', self.star_offsets, ur)
                delta_mag = np.sqrt(2 * self.G * self.M_bh /
                                    r) * (proj / self.star_radius)
                delta_vel = delta_mag[:, None] * ur[None, :]
                self.particles_vel += delta_vel
            else:
                # Rigid body: update positions
                self.update_particles_pos()
        else:
            # Update each particle (vectorized for efficiency)
            r_vecs = self.particles_pos - self.bh_position[None, :]
            rs = np.linalg.norm(r_vecs, axis=1)[:, None]
            accs = -self.G * self.M_bh / (rs**2 + self.eps**2)**1.5 * r_vecs
            self.particles_vel += accs * dt
            self.particles_pos += self.particles_vel * dt

            # Compute energies with softening (for consistency)
            vs2 = np.sum(self.particles_vel ** 2, axis=1)[:, None]
            pot = -self.G * self.M_bh / np.sqrt(rs**2 + self.eps**2)
            es = 0.5 * vs2 + pot
            bound = (es < 0)[:, 0]

            # Viscosity for radial velocity only (spiral infall without suction, circularization)
            # Configurable: coefficient (higher for faster circularization, 0.05 for quick)
            alpha = 0.0001
            if np.any(bound):
                ur_bound = r_vecs[bound, :] / rs[bound, :]
                v_r = np.einsum(
                    'ij,ij->i', self.particles_vel[bound], ur_bound)[:, None]
                self.particles_vel[bound] -= alpha * v_r * ur_bound

        self.particles = self.particles_pos

    def update_particles_pos(self):
        self.particles_pos = self.star_center[None, :] + self.star_offsets
