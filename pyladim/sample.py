# -*- coding: utf-8 -*-

"""Utilities functions for sampling output from the ROMS

Horizontal sampling
-------------------

:func:`sample2D`
  Sample a 2D field given at rho-points
:func:`sample2DU`
  Sample a 2D field given at u-points
:func:`sample2DV`
  Sample a 2D field given at v-points

"""

# -----------------------------------
# Bjørn Ådlandsvik, bjorn@imr.no
# Institute of Marine Research
# Bergen, Norway
# 2010-09-30
# -----------------------------------

import datetime
import numpy as np

# ---------------------


def sample2D2(F, X, Y):
    """Bilinear sample of a 2D field

    *F* : 2D array

    *X*, *Y* : position in grid coordinates, scalars or compatible arrays

    Note reversed axes, for integers i and j we have
      ``sample2D(F, i, j) = F[j,i]``

    Using linear interpolation

    """

    Z = np.add(X, Y)     # Test for compatibility
    if np.isscalar(Z):  # Both X and Y are scalars
        I = int(X)
        J = int(Y)
        P = X - I
        Q = Y - J
    else:
        # Make arrays of common shape
        X0 = X + np.zeros_like(Z)
        Y0 = Y + np.zeros_like(Z)
        I = X0.astype('int')
        J = Y0.astype('int')
        P = X0 - I
        Q = Y0 - J

    W00 = (1-P)*(1-Q)
    W01 = (1-P)*Q
    W10 = P*(1-Q)
    W11 = P*Q

    return W00*F[J,I] + W01*F[J+1,I] + W10*F[J,I+1] + W11*F[J+1,I+1]

# --------------------------------------------------


def sample2DU(F, X, Y):
    return sample2D(F, X-0.5, Y)

# --------------------------------------------------


def sample2DV(F, X, Y):
    return sample2D(F, X, Y-0.5)

# -------------------------------------------------


def sample2D_masked(F, M, X, Y):
    """Bilinar sample of a 2D field

    F = 2D array, M = mask (=1 on sea, = 0 on land)
    X, Y = position in grid coordinates, scalars or compatible arrays

    Note reversed axes, for integers i and j we have
    sample2D(F, i, j) = F[j,i]

    Using linear interpolation

    """

    masked = True

    Z = np.add(X, Y)     # Test for compatibility
    if np.isscalar(Z):  # Both X and Y are scalars
        I = int(X)
        J = int(Y)
        P = X - I
        Q = Y - J
    else:
        # Make arrays of common shape
        X0 = X + np.zeros_like(Z)
        Y0 = Y + np.zeros_like(Z)
        I = X0.astype('int')
        J = Y0.astype('int')
        P = X0 - I
        Q = Y0 - J

    W00 = M[J,I]*(1-P)*(1-Q)
    W01 = M[J+1,I]*(1-P)*Q
    W10 = M[J,I+1]*P*(1-Q)
    W11 = M[J+1,I+1]*P*Q
    if masked:
        W00 = M[J,I]     * W00
        W01 = M[J+1,I]   * W01
        W10 = M[J,I+1]   * W10
        W11 = M[J+1,I+1] * W11
    SW = W00 + W01 + W10 + W11
    F_interp = np.where(SW > 0,
            (W00*F[J,I] + W01*F[J+1,I] + W10*F[J,I+1] + W11*F[J+1,I+1])/SW,
             0.0)
    #F_interp = np.ma.masked_where(SW == 0, F_interp)

    return F_interp

# ------------------

def sample2D(F, X, Y, mask=None, undef_value=0.0, outside_value=None):
    """Bilinear sample of a 2D field

    *F* : 2D array

    *X*, *Y* : position in grid coordinates, scalars or compatible arrays

    *mask* : if present must be a 2D matrix with 1 at valid
             and zero at non-valid points

    *undef_value* : value to put at undefined points

    *outside_value* : value to return outside the grid
                defaults to None,
                raising ValueError if any points are outside

    Note reversed axes, for integers i and j we have
      ``sample2D(F, i, j) = F[j,i]``

    If jmax, imax = F.shape
    then inside values requires 0 <= x < imax-1, 0 <= y < jmax-1

    Using bilinear interpolation

    """

    # --- Argument checking ---

    # X and Y should be broadcastable to the same shape
    Z = np.add(X, Y)
    # scalar is True if both X and Y are scalars
    scalar = np.isscalar(Z)

    if np.rank(F) != 2:
        raise ValueError("F must be 2D")
    if mask is not None:
        if mask.shape != F.shape:
            raise ValueError("Must have mask.shape == F.shape")

    jmax, imax = F.shape

    # Broadcast X and Y
    X0 = X + np.zeros_like(Z)
    Y0 = Y + np.zeros_like(Z)
    # Find integer I, J such that
    # 0 <= I <= X < I+1 <= imax-1, 0 <= J <= Y < J+1 <= jmax-1
    # and local increments P and Q
    I = X0.astype('int')
    J = Y0.astype('int')
    P = X0 - I
    Q = Y0 - J

    outside = (X0 < 0) | (X0 >= imax-1) | (Y0 < 0) | (Y0 >= jmax-1)
    if np.any(outside):
        if outside_value is None:
            raise ValueError("point outside grid")
        I = np.where(outside, 0, I)
        J = np.where(outside, 0, J)
        # try:
        #    J[outside] = 0
        #    I[outside] = 0
        # except TypeError:    # Zero-dimensional
        #    I = np.array(0)
        #    J = np.array(0)

    # Weights for bilinear interpolation
    W00 = (1-P)*(1-Q)
    W01 = (1-P)*Q
    W10 = P*(1-Q)
    W11 = P*Q
    SW = 1.0   # Sum of weigths

    if mask is not None:
        W00 = mask[J, I]     * W00
        W01 = mask[J+1, I]   * W01
        W10 = mask[J, I+1]   * W10
        W11 = mask[J+1, I+1] * W11
        SW = W00 + W01 + W10 + W11

    SW = np.where(SW==0, -1.0, SW)  # Avoid division by zero below
    S = np.where(SW <= 0, undef_value,
          (W00*F[J,I] + W01*F[J+1,I] + W10*F[J,I+1] + W11*F[J+1,I+1])/SW)

    # Set in outside_values
    if outside_value:
        S = np.where(outside, outside_value, S)

#   Scalar input gives scalar output
    if scalar:
        S = float(S)

    return S

# -----------------------------------------


def bilin_inv(f, g, F, G, maxiter=7, tol=1.0e-7):
    """Inverse bilinear interpolation

    f, g : scalars or arrays of same shape
    F, G : 2D arrays of the same shape

    returns x, y : shaped like f and g
    such that F and G linearly interpolated to x, y
    returns f and g

    """

    imax, jmax = F.shape
    if G.shape != (imax, jmax):
        raise ValueError("Shape mismatch in 2D arrays")

    scalar = np.isscalar(f)

    if scalar:
        if not np.isscalar(g):
            raise ValueError(
                "Target values must both be scalars or both arrays")
        # initial guess = mid point
        x = 0.5*imax
        y = 0.5*jmax

    else: # vector target
        f = np.asarray(f)
        g = np.asarray(g)
        fshape = f.shape
        if g.shape != fshape:
            raise ValueError("Target arrays must have the same shape")
        # Make 1D
        # f = f.ravel()
        # g = g.ravel()

        # initial guess
        x = np.zeros_like(f) + 0.5*imax
        y = np.zeros_like(f) + 0.5*jmax

    for t in range(maxiter):

        if scalar:
            i = int(x)
            j = int(y)
        else:
            i = x.astype('i')
            j = y.astype('i')

        p, q = x - i, y - j

        # Bilinear estimate of F[x,y] and G[x,y]
        Fs = (1-p)*(1-q)*F[i,j] + p*(1-q)*F[i+1,j] + \
             (1-p)*q*F[i,j+1] + p*q*F[i+1,j+1]
        Gs = (1-p)*(1-q)*G[i,j] + p*(1-q)*G[i+1,j] + \
             (1-p)*q*G[i,j+1] + p*q*G[i+1,j+1]

        H = (Fs - f)**2 + (Gs - g)**2
        # print t, H
        if np.all(H < tol):
            break

        # Estimate Jacobi matrix
        Fx = (1-q)*(F[i+1,j]-F[i,j]) + q*(F[i+1,j+1]-F[i,j+1])
        Fy = (1-p)*(F[i,j+1]-F[i,j]) + p*(F[i+1,j+1]-F[i+1,j])
        Gx = (1-q)*(G[i+1,j]-G[i,j]) + q*(G[i+1,j+1]-G[i,j+1])
        Gy = (1-p)*(G[i,j+1]-G[i,j]) + p*(G[i+1,j+1]-G[i+1,j])

        # Newton-Raphson step
        # Jinv = np.linalg.inv([[Fx, Fy], [Gx, Gy]])
        # incr = - np.dot(Jinv, [Fs-f, Gs-g])
        # x = x + incr[0], y = y + incr[1]
        det = Fx*Gy - Fy*Gx
        x = x - ( Gy*(Fs-f) - Fy*(Gs-g)) / det
        y = y - (-Gx*(Fs-f) + Fx*(Gs-g)) / det

    return x, y

# ----------------------------
