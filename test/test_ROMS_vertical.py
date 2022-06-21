import numpy as np
from ladim1.gridforce.ROMS import sdepth, z2s, sample3D


# Make a module level fixture for these tests


def test_z2s():
    # Set-up
    kmax = 30
    H = 100.0 + np.zeros((2, 2))
    Hc = 10.0
    # Make a random increasing sequence of N values between -1 to 0
    C = np.random.uniform(-1, 0, kmax)
    C.sort()
    # C = np.linspace(-1, 0, kmax + 2)[1:-1]  # Exclude end points
    z_rho = sdepth(H, Hc, C, stagger="rho")
    assert np.all((-100 < z_rho) & (z_rho < 0))
    X, Y = np.array([0.5]), np.array([0.5])
    I = np.round(X).astype(int)
    J = np.round(Y).astype(int)
    z_r = z_rho[:, J, I]  # z_rho on the grid cells containint the particles

    def atest(Z):
        K, A = z2s(z_rho, X, Y, np.array([Z]))
        assert K.dtype == "int64"
        assert all((1 <= K) & (K < kmax))
        assert all((z_r[K - 1] <= -Z) | (K == 1))
        assert all((-Z <= z_r[K]) | (K == kmax - 1))
        assert all((0 <= A) & (A <= 1))
        # Linear interpolation in the interior
        assert all(
            (np.abs(A * z_r[K - 1] + (1 - A) * z_r[K] + Z) < 1e-6)
            | (-Z < z_r[0])
            | (-Z > z_r[-1])
        )
        # Extend constant above upper limit
        assert all(
            (-Z <= z_r[-1])
            | (np.abs(A * z_r[K - 1] + (1 - A) * z_r[K] - z_r[-1]) < 1e-6)
        )
        # Extend constant below lower limit
        assert all(
            (-Z >= z_r[0]) | (np.abs(A * z_r[K - 1] + (1 - A) * z_r[K] - z_r[0]) < 1e-6)
        )

    atest(50)  # Mid depth
    atest(0)  # Surface
    atest(100)  # Bottom
    atest(0.1)  # Near surface
    atest(99.9)  # Near bottom
    atest(1000)  # Below bottom
    atest(-10)  # Above surface


def test_sample3D():
    # Set-up
    kmax = 30
    H = 100.0 + np.zeros((2, 2))
    Hc = 10.0
    # Make a random increasing sequence of N values between -1 to 0
    C = np.linspace(-1, 0, kmax + 2)[1:-1]  # Exclude end points
    z_rho = sdepth(H, Hc, C, stagger="rho")
    assert np.all((-100 < z_rho) & (z_rho < 0))
    X, Y = np.array(4 * [0.5]), np.array(4 * [0.5])
    I = np.round(X).astype(int)
    J = np.round(Y).astype(int)
    Z = np.array([0, 20, 50, 100])
    K, A = z2s(z_rho, X, Y, Z)
    I = np.round(X).astype(int)
    J = np.round(Y).astype(int)
    z_r = z_rho[:, J, I]  # z_rho on the grid cells containint the particles

    # Interpolate 3D field z_rho, shall give Z, except near surface and bottom
    V = sample3D(z_rho, X, Y, K, A, method="bilinear")
    assert V[0] == z_r[-1, 0]  # -Z > z_rho[-1]
    assert V[1] == -Z[1]
    assert V[2] == -Z[2]
    assert V[3] == z_r[0, 3]  # -Z < z_rho[0]
