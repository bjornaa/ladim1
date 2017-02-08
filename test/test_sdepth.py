# -*- coding: utf-8 -*-

"""Unit tests for the vertical depth functions for ROMS grid"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# ----------------------------------

import unittest
import numpy as np

from ladim.grid import sdepth, s_stretch, Z2S

# ------------------------------------


class test_sdepth(unittest.TestCase):
    """Test the sdepth function"""

    def setUp(self):
        """Setup unstretched and stretched vertical scales"""
        N = 10
        # Make N uniformly distributed values from -1+0.5/N to -0.5/N
        self.S = -1.0 + (0.5 + np.arange(N)) / N
        # Make a random increasing sequence of N values between -1 to 0
        self.C_random = np.random.uniform(-1, 0, N)
        self.C_random.sort()

    def test1D_unstretched(self):
        """C = S should give equally distributed sigma-coordinates"""
        H = 100.0
        Hc = 10.0
        C = self.S
        Z = sdepth(H, Hc, C)
        self.assertTrue(np.allclose(Z, H*C))

    def test_hc_is_zero(self):
        """Hc = 0 should give only the stretched values"""
        H = 100.0
        Hc = 0.0
        C = self.C_random
        Z = sdepth(H, Hc, C)
        self.assertTrue(np.allclose(Z, H*C))

    def test_hc_is_h(self):
        """Hc = H should remove effect of stretching"""
        H = 100.0
        Hc = H
        S = self.S
        C = self.C_random
        Z = sdepth(H, Hc, C)
        self.assertTrue(np.allclose(Z, H*S))

    def test_shape(self):
        # Test that the shape comes out correctly
        H = np.array([[100.0, 90.0, 80.0], [70.0, 70.0, 60.0]])
        Hc = 10.0
        C = self.C_random
        Z = sdepth(H, Hc, C)
        Mp, Lp = H.shape
        self.assertEqual(Z.shape, (len(C), Mp, Lp))

# -------------------------------------------------


class test_sdepth_Vtransform2(unittest.TestCase):

    def test1D_unstretched(self):
        H = 100.0
        Hc = 10.0
        N = 10
        C = -1.0 + (0.5+np.arange(N))/N  # equally distributed
        Z = sdepth(H, Hc, C, Vtransform=2)
        # Z should now be equally distributed
        # Z = A = array([-95.0,-85.0, ..., -5.0])
        A = np.arange(-95.0, -4.0, 10.0)
        self.assertTrue(np.allclose(Z, A))

    def test_hc_is_zero(self):
        # With Hc = 0, just scaled sc_r scaled by H
        H = 100.0
        Hc = 0.0
        N = 10
        cs_r = (-1.0 + (0.5+np.arange(N))/N)**3
        Z = sdepth(H, Hc, cs_r, Vtransform=2)
        A = H*cs_r
        self.assertTrue(np.allclose(Z, A))

    def test_hc_is_h(self):
        # With Hc = H, mean of stretched and unstretched
        H = 100.0
        Hc = H
        N = 10
        S = -1.0 + (0.5+np.arange(N))/N
        C = S**3
        Z = sdepth(H, Hc, C, Vtransform=2)
        self.assertTrue(np.allclose(Z, 0.5*H*(S+C)))

    def test_shape(self):
        # Test that the shape comes out correctly
        H = np.array([[100.0, 90.0, 80.0], [70.0, 70.0, 60.0]])
        Hc = 10.0
        N = 10
        S = -1.0 + (0.5+np.arange(N))/N
        C = S**3
        Z = sdepth(H, Hc, C, Vtransform=2)
        Mp, Lp = H.shape
        self.assertEqual(Z.shape, (N, Mp, Lp))

# ------------------------


class test_s_stretch(unittest.TestCase):

    def test_valid_output(self):
        """For rho-points C should obey -1 < C[i] < C[i+1] < 0"""
        N = 30
        theta_s = 6.0
        theta_b = 0.6
        C = s_stretch(N, theta_s, theta_b)
        Cp = np.concatenate(([-1], C, [0]))
        D = np.diff(Cp)
        self.assertTrue(np.all(D > 0))
        self.assertEqual(len(C), N)

    def test_valid_output_w(self):
        """For w-points C should obey -1 < C[i+1] < 0"""
        N = 30
        theta_s = 6.0
        theta_b = 0.6
        C = s_stretch(N, theta_s, theta_b, stagger='w')
        # Check increasing
        self.assertTrue(np.all(np.diff(C) > 0))
        # End points
        self.assertEqual(C[0], -1.0)
        self.assertEqual(C[-1], 0.0)
        # Length
        self.assertEqual(len(C), N+1)


class test_Vstretching4(unittest.TestCase):

    def test_valid_output(self):
        """For rho-points C should obey -1 < C[i] < C[i+1] < 0"""
        N = 30
        theta_s = 6.0
        theta_b = 0.6
        C = s_stretch(N, theta_s, theta_b, Vstretching=4)
        Cp = np.concatenate(([-1], C, [0]))
        D = np.diff(Cp)
        self.assertTrue(np.all(D > 0))
        self.assertEqual(len(C), N)

    def test_valid_output_w(self):
        """For w-points C should obey -1 < C[i+1] < 0"""
        N = 30
        theta_s = 6.0
        theta_b = 0.6
        C = s_stretch(N, theta_s, theta_b, Vstretching=4, stagger='w')
        # Check increasing
        self.assertTrue(np.all(np.diff(C) > 0))
        # End points
        self.assertEqual(C[0], -1.0)
        self.assertEqual(C[-1], 0.0)
        # Length
        self.assertEqual(len(C), N+1)


class test_Z2S(unittest.TestCase):

    def test_correct(self):
        N = 30
        H = 100 + np.zeros((1, 1))
        Hc = 10.0
        # Make a random increasing sequence of N values between -1 to 0
        C = np.random.uniform(-1, 0, N+1)
        C.sort()
        Z = 50.0
        z_w = sdepth(H, Hc, C, stagger='w')
        assert(z_w.shape == (31, 1, 1))
        K, A = Z2S(z_w, 0.5, 0.5, Z)
        # assert(K == 3)
        assert(z_w[K] <= -Z)
        assert(-Z <= z_w[K+1])
        assert(0 <= A <= 1)
        assert(A == 3.14)
        assert(A*z_w[K] + (1-A)*z_w[K+1] == -Z)


# ----------------------------------------------------

    # def test_linear_interpolation(self):
    #     """The interpolation is linear"""
    #     z_r = np.linspace(-95, -5, 10)
    #     F = np.random.random(z_r.shape)
    #     a, b = 0.3, 0.7 # sum = 1
    #     k = 4
    #     z = a*z_r[k-1] + b*z_r[k]
    #     v = a*F[k-1] + b*F[k]
    #     self.assertAlmostEqual(zslice(F, z_r, z), v)
    #
    # def test_extrapolate(self):
    #     """Extrapolation should extend highest and lowest values"""
    #     z_r = np.linspace(-95, -5, 10)
    #     F = np.random.random(z_r.shape)
    #     z = -2.0     # z > z_r[-1]
    #     self.assertEqual(zslice(F, z_r, z), F[-1]) # high value
    #     z = -122.3   # z < z_r[0]
    #     self.assertEqual(zslice(F, z_r, z), F[0])  # low value
    #
    # def test_interp(self):
    #     """zslice of 1D field is np.interp"""
    #     z_r = np.linspace(-95, -5, 10)
    #     F = np.random.random(z_r.shape)
    #     z = -52.0
    #     self.assertAlmostEqual(zslice(F, z_r, z), np.interp(z, z_r, F))
    #
    # def test_non_equidistant(self):
    #     """zslice should work with non-equidistand z_r"""
    #     # Make a random increasing sequence z_r between -100 and 0
    #     z_r = -100 * np.random.rand(10)
    #     z_r.sort()
    #     F = np.random.rand(10)
    #     z = -52.0
    #     self.assertAlmostEqual(zslice(F, z_r, z), np.interp(z, z_r, F))
    #
    #
    # def test_shapes_OK(self):
    #     """Correct input shapes gives correct output shape"""
    #
    #     # Make a z_r array of shape (N, Mp, Lp)
    #     # in this case (10,3,2)
    #     K = np.linspace(-95, -5, 10)
    #     z_r = np.transpose([[K, 2*K, K], [K, 0.7*K, 1.2*K]])
    #     # F has same shape
    #     F = np.random.random(z_r.shape)
    #     # Scalar z
    #     z = -52.0
    #     self.assertEqual(zslice(F,z_r,z).shape, z_r.shape[1:])
    #     # Horizontal z with shape z_r.shape[1:] = (Mp, Lp)
    #     z =  np.array([-10.2, -14., -28, -2.4, -88.7, -122])
    #     z.shape = (3,2)  # z has correct shape
    #     self.assertEqual(zslice(F,z_r,z).shape, z_r.shape[1:])
    #
    # def test_Fshape_wrong(self):
    #     """Raise exception if F.shape != z_r.shape"""
    #
    #     # Make a z_r array of shape (N, Mp, Lp)
    #     # in this case (10,3,2)
    #     K = np.linspace(-95, -5, 10)
    #     z_r = np.transpose([[K, 2*K, K], [K, 0.7*K, 1.2*K]])
    #     # F has same shape
    #     F = np.random.random(z_r.shape)
    #     F.shape  = (10,2,3)  # Give F wrong shape
    #     z = -52.0
    #     self.assertRaises(ValueError, zslice, F, z_r, z)
    #
    # def test_zshape_wrong(self):
    #     """Raise exception if z.shape is wrong"""
    #
    #     # Make a z_r array of shape (N, Mp, Lp)
    #     # in this case (10,3,2)
    #     K = np.linspace(-95, -5, 10)
    #     z_r = np.transpose([[K, 2*K, K], [K, 0.7*K, 1.2*K]])
    #     # F has same shape
    #     F = np.random.random(z_r.shape)
    #     z =  np.array([-10.2, -14., -28, -2.4, -88.7, -122])
    #     z.shape = (2,3)   # z is 2D, correct size, wrong shape
    #     self.assertRaises(ValueError, zslice, F, z_r, z)
    #
    # def test_array_values(self):
    #     """Test that interpolation gives correct results with array input"""
    #     # Make a z_r array of shape (N, Mp, Lp)
    #     # in this case (10,3,2)
    #     K = np.linspace(-95, -5, 10)
    #     z_r = np.transpose([[K, 2*K, K], [K, 0.7*K, 1.2*K]])
    #     # F has same shape
    #     F = np.random.random(z_r.shape)
    #     j, i = 2, 1
    #     z = -52.0                # z is scalar
    #     Fz = zslice(F, z_r, z)
    #     self.assertAlmostEqual(Fz[j,i], np.interp(z, z_r[:,j,i], F[:,j,i]))
    #
    #     z =  np.array([-10.2, -14., -28, -2.4, -88.7, -122])
    #     z.shape = (3,2)  # z has correct shape
    #     Fz = zslice(F, z_r, z)
    #     self.assertAlmostEqual(Fz[j,i],
    #                            np.interp(z[j,i], z_r[:,j,i], F[:,j,i]))


# --------------------------------------

if __name__ == '__main__':
    unittest.main()
