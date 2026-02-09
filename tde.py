# tde.py

import numpy as np


class TDE:
    def __init__(self, bh_position, M_bh):
        # BH parameters
        self.bh_position = bh_position
        self.M_bh = M_bh
        self.G = 0.5  # Gravitational constant (simulation units)
        # Softening length to prevent singularity and infall (~ inner_radius / 2 rec)
        self.eps = 5

        # TDE states
        self.active = False
        self.moving = False
        self.disrupted = False

        # for the bound/unbound
        self.initial_energy = None
        self.initial_bound_mask = None

        # Star and particle parameters
        self.num_particles = 90000  # number of star particles
        self.star_mass = None
        self.star_radius = None
        self.Rt = None
        self.star_center = None
        self.star_vel = None
        self.star_offsets = None
        self.particles_pos = None
        self.particles_vel = None
        self.particles = None
        self.colors = None  # base particle colors
        self.flicker_phases = None  # flicker phases (like background stars)

        # disk settle
        self.disk_plane_normal = np.array([0.0, 0.0, 1.0])  # disk
        self.disk_settle_alpha = 0.0002  # settle velocity
        self.disk_outer_limit = 50.0  # max radius
        self.disk_outer_decay = 0.999  # gradual settling to existing disk
        self.orbit_counter = np.zeros(
            self.num_particles)  # turn orbits
        # предыдущие углы для подсчёта оборотов
        self.last_angles = np.zeros(self.num_particles)
        self.settle_orbits = 15.0  # number of turns before settling

        # star's disk parameters
        self.disk_base_height = 3.0
        self.disk_heat_factor = 4.0

        # Spaghettification (pre-disruption only)
        self.spaghettify_strength = 2   # strength
        self.spaghettify_power = 2.0         # increase with approach
        self.spaghettify_max_stretch = 10.0   # max stretch
        self.spaghettify_compress = 0.4     # compress strength

        # tidal torque
        self.tidal_torque_strength = 0.3

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
        beta = 3.0  # rt/rp
        Rp = self.Rt / beta

        # Initial distance
        r = r_init

        # Parabolic orbit parameters (e=1)
        p = 2 * Rp
        cos_nu = p / r - 1
        # initial_angle to shift position/trajectory
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
        v_theta = v_theta

        # less velocity for proper spaghettification
        v_r *= 0.5      # rad velocity
        v_theta *= 0.8  # tang velocity

        # Velocity components (ccw rotation like disk; right-side approach with left curl)
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

        # Flicker phases
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
            # 1.5–2.0 (higher = stronger gravity)
            acc = -1.8 * self.G * self.M_bh / (r**2 + self.eps**2)**1.5 * r_vec
            self.star_vel += acc * dt
            self.star_center += self.star_vel * dt

            # SPAGETTIFICATION (before disruption only)
            r_vec = self.star_center - self.bh_position
            r = np.linalg.norm(r_vec) + 1e-8
            ur = r_vec / r

            # gradual increase
            stretch_factor = 1 / (1 + (r / self.Rt) ** self.spaghettify_power)

            stretch_factor *= self.spaghettify_strength
            stretch_factor = np.clip(
                stretch_factor, 0.0, self.spaghettify_max_stretch)

            #  offsets
            proj = np.dot(self.star_offsets, ur)[:, None] * ur[None, :]
            perp = self.star_offsets - proj

            # tidal deformation
            deformed_offsets = (
                proj * (1 + 3 * stretch_factor) +
                perp * (1 - 0.5 * self.spaghettify_compress * stretch_factor))\

            # TIDAL TORQUE (small internal rotation)
            # orbital momentum
            L_dir = np.cross(r_vec, self.star_vel)
            L_norm = np.linalg.norm(L_dir) + 1e-8
            L_dir /= L_norm
            # internal rotation axis (perpendicular to r_vec)
            torque_dir = np.cross(L_dir, ur)
            torque_dir /= np.linalg.norm(torque_dir) + 1e-8
            # rotation angle
            theta = self.tidal_torque_strength * stretch_factor * \
                dt
            # Rodrigues formula: rotate every offset around torque_dir
            k = torque_dir
            v = deformed_offsets  # Nx3
            v_rot = (v * np.cos(theta) +
                     np.cross(k, v) * np.sin(theta) +
                     k[None, :] * np.einsum('ij,j->i', v, k)[:, None] * (1 - np.cos(theta)))
            deformed_offsets = v_rot

            # update particle positions
            self.particles_pos = self.star_center[None, :] + deformed_offsets

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
                # Freeze energy distribution after disruption
                r_vecs = self.particles_pos - self.bh_position
                rs = np.linalg.norm(r_vecs, axis=1)

                vs2 = np.sum(self.particles_vel**2, axis=1)
                pot = -self.G * self.M_bh / np.sqrt(rs**2 + self.eps**2)

                self.initial_energy = 0.5 * vs2 + pot
                self.initial_bound_mask = self.initial_energy < 0

        else:
            # Update each particle (vectorized for efficiency)
            r_vecs = self.particles_pos - self.bh_position[None, :]
            rs = np.linalg.norm(r_vecs, axis=1)[:, None]

            # BH barrier (to not to fall to BH earlier)
            inner_barrier = 3.5
            mask_inner = rs[:, 0] < inner_barrier
            if np.any(mask_inner):
                push = r_vecs[mask_inner] / (rs[mask_inner] + 1e-6)
                self.particles_vel[mask_inner] += 0.0015 * \
                    push  # inner barrier

            accs = -self.G * self.M_bh / (rs**2 + self.eps**2)**1.5 * r_vecs
            self.particles_vel += accs * dt
            self.particles_pos += self.particles_vel * dt

            # freezed bound/unbound
            E = self.initial_energy
            bound = self.initial_bound_mask
            # gradual stop (pre-bound)
            E_scale = 0.12  # настраиваемый коэффициент
            disk_weight = np.exp(-np.maximum(E, 0) / E_scale)
            mask_disk = disk_weight > 0.001  # for pre-bound

            # THICK DISK MODEL
            if np.any(mask_disk):

                r_bound = rs[mask_disk][:, 0]

                target_height = (
                    self.disk_base_height
                    + self.disk_heat_factor * np.exp(-r_bound / 30))

                z = self.particles_pos[mask_disk, 2]
                v_z = self.particles_vel[mask_disk, 2]

                self.particles_vel[mask_disk, 2] -= (
                    0.0005 * (z / (target_height + 1e-6))
                    + 0.001 * v_z)

            # Turns count and final settle to exisiting disk
            # angles for ALL particles
            angles_all = np.arctan2(
                self.particles_pos[:, 1],
                self.particles_pos[:, 0])
            delta_angle = angles_all - self.last_angles
            delta_angle = (delta_angle + np.pi) % (2*np.pi) - np.pi
            # increase for bound only
            self.orbit_counter[bound] += np.abs(delta_angle[bound])
            # update for ALL
            self.last_angles = angles_all

            # Viscosity for radial velocity only (spiral infall without suction, circularization)
            # higher for faster circularization
            alpha = 0.0002

            # orbital stabilization (to not to fall straight to bh)
            r_bound = rs[mask_disk]
            v_bound = self.particles_vel[mask_disk]
            r_vec_bound = r_vecs[mask_disk]
            # tang direction
            ur = r_vec_bound / r_bound
            vt = v_bound - np.sum(v_bound * ur, axis=1)[:, None] * ur
            # circular velocity
            v_circ = np.sqrt(self.G * self.M_bh / r_bound)
            vt_norm = np.linalg.norm(vt, axis=1) + 1e-8
            vt_dir = vt / vt_norm[:, None]
            # slowly to the circular orbit
            beta_circ = 0.0012  # circularization
            self.particles_vel[mask_disk] += beta_circ * (
                v_circ * vt_dir - vt)

            if np.any(mask_disk):
                ur_bound = r_vecs[mask_disk, :] / rs[mask_disk, :]

                v_bound = self.particles_vel[mask_disk]

                v_r = np.einsum('ij,ij->i', v_bound, ur_bound)[:, None]

                vt = v_bound - v_r * ur_bound

                self.particles_vel[mask_disk] -= alpha * v_r * ur_bound
                self.particles_vel[mask_disk] -= 0.1 * \
                    alpha * vt  # tang velocity damping

                # disk cooling (slow energy loss)
                cool = 0.00005
                self.particles_vel[mask_disk] *= (1 - cool)

        self.particles = self.particles_pos

    def update_particles_pos(self):
        self.particles_pos = self.star_center[None, :] + self.star_offsets
