# -*- coding: utf-8 -*-

"""Unit tests for the vertical depth functions for ROMS grid"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# ----------------------------------

import unittest
import numpy as np

from ladim.gridforce.ROMS import sdepth, s_stretch, z2s


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
        self.assertTrue(np.allclose(Z, H * C))

    def test_hc_is_zero(self):
        """Hc = 0 should give only the stretched values"""
        H = 100.0
        Hc = 0.0
        C = self.C_random
        Z = sdepth(H, Hc, C)
        self.assertTrue(np.allclose(Z, H * C))

    def test_hc_is_h(self):
        """Hc = H should remove effect of stretching"""
        H = 100.0
        Hc = H
        S = self.S
        C = self.C_random
        Z = sdepth(H, Hc, C)
        self.assertTrue(np.allclose(Z, H * S))

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
        C = -1.0 + (0.5 + np.arange(N)) / N  # equally distributed
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
        cs_r = (-1.0 + (0.5 + np.arange(N)) / N) ** 3
        Z = sdepth(H, Hc, cs_r, Vtransform=2)
        A = H * cs_r
        self.assertTrue(np.allclose(Z, A))

    def test_hc_is_h(self):
        # With Hc = H, mean of stretched and unstretched
        H = 100.0
        Hc = H
        N = 10
        S = -1.0 + (0.5 + np.arange(N)) / N
        C = S ** 3
        Z = sdepth(H, Hc, C, Vtransform=2)
        self.assertTrue(np.allclose(Z, 0.5 * H * (S + C)))

    def test_shape(self):
        # Test that the shape comes out correctly
        H = np.array([[100.0, 90.0, 80.0], [70.0, 70.0, 60.0]])
        Hc = 10.0
        N = 10
        S = -1.0 + (0.5 + np.arange(N)) / N
        C = S ** 3
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
        C = s_stretch(N, theta_s, theta_b, stagger="w")
        # Check increasing
        self.assertTrue(np.all(np.diff(C) > 0))
        # End points
        self.assertEqual(C[0], -1.0)
        self.assertEqual(C[-1], 0.0)
        # Length
        self.assertEqual(len(C), N + 1)


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
        C = s_stretch(N, theta_s, theta_b, Vstretching=4, stagger="w")
        # Check increasing
        self.assertTrue(np.all(np.diff(C) > 0))
        # End points
        self.assertEqual(C[0], -1.0)
        self.assertEqual(C[-1], 0.0)
        # Length
        self.assertEqual(len(C), N + 1)
