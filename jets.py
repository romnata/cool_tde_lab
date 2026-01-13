import numpy as np


def generate_jet_particles(
    num_particles=3000,
    length=120.0,
    base_sigma=0.5,
    expansion_rate=2.5,
    axial_offset=0.0,
    axis=(0.0, 0.0, 1.0),
    color_profile='white_to_red'
):
    """
    Generates jet particles (two opposite streams).
    Returns ndarray shape (2*num_particles, 7): x,y,z, r,g,b, size

    Parameters:
      num_particles -- particles per stream
      length        -- max stream length (by |z| in its own system)
      base_sigma    -- base dispersion radius (small value -> narrow base)
      expansion_rate-- sigma growth factor along stream: sigma(z) = base_sigma * (1 + expansion_rate * (z/length))
      axial_offset  -- z-offset for jet start
      axis          -- jet axis direction (vector), default +z
      color_profile -- 'white_to_red' or 'white_to_yellow' (controls color gradient)
    """

    # z in [0, length] along +stream
    z = np.random.uniform(0.0, length, num_particles)
    # Radial spread: normal distribution with sigma depending on z
    sigma = base_sigma * (1.0 + expansion_rate * (z / length))
    # Radial coordinates in cross-section plane
    x = np.random.normal(0.0, sigma)
    y = np.random.normal(0.0, sigma)

    t = z / length  # 0..1

    # Color gradient
    if color_profile == 'white_to_red':
        r = 1.0 - 0.2 * t  # R: near 1 -> slight drop
        g = 1.0 - 0.9 * t  # G: drops faster -> white to red
        b = 1.0 - 1.0 * t  # B: drops to ~0
    elif color_profile == 'white_to_yellow':
        r = 1.0 - 0.1 * t
        g = 1.0 - 0.5 * t
        b = 1.0 - 0.9 * t

    elif color_profile == 'white_blue_to_red':
        # Base (t=0): bluish white-blue (r=0.7, g=0.8, b=1.0)
        # Middle (t~0.5): enhanced blue (r=0.5, g=0.6, b=1.0)
        # End (t=1): red (r=1.0, g=0.2, b=0.1) — for knots/shocks
        r = 0.7 - 0.9 * t + 1.2 * t**2  # Starts at 0.7, drops, then rises to red
        g = 0.8 + 0.4 * t - 1.0 * t**2  # Drops from 0.8 to 0.2, slow at start
        # High (1.0) to middle, then drops to 0.1
        b = 1.0 + 0.8 * t - 1.8 * t**2

    else:
        # fallback neutral fade
        r = 1.0 - 0.5 * t
        g = 1.0 - 0.5 * t
        b = 1.0 - 0.5 * t

    # Particle size (visual), slightly larger with z
    sizes = np.clip(1.0 + 2.5 * t, 0.5, 6.0)

    # Assemble upper stream array: offset by axial_offset
    jet_up = np.column_stack((x, y, z + axial_offset, r, g, b, sizes))

    # Lower stream — mirrored by z
    jet_down = np.column_stack((x, y, -z + axial_offset, r, g, b, sizes))

    particles = np.vstack((jet_up, jet_down))

    # Rotate jet axis to arbitrary vector `axis` if needed
    ax = np.asarray(axis, dtype=float)
    ax_norm = np.linalg.norm(ax)
    if ax_norm == 0 or np.allclose(ax, [0, 0, 1]):
        return particles.astype(float)

    ax = ax / ax_norm
    # Compute rotation matrix from (0,0,1) to ax using Rodrigues' formula
    k = np.cross([0.0, 0.0, 1.0], ax)
    k_norm = np.linalg.norm(k)
    if k_norm < 1e-8:
        return particles.astype(float)  # Axes nearly aligned
    k = k / k_norm
    cos_theta = np.dot([0.0, 0.0, 1.0], ax)
    theta = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    K = np.array([[0, -k[2], k[1]],
                  [k[2], 0, -k[0]],
                  [-k[1], k[0], 0]], dtype=float)
    R = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

    coords = particles[:, :3].T  # 3 x N
    rotated = (R @ coords).T
    particles[:, :3] = rotated

    return particles.astype(float)
