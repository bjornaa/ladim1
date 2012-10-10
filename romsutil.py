# -*- coding: utf-8 -*-

import numpy as np


def sdepth(H, Hc, C, stagger="rho", Vtransform=1):
    """Return depth of rho-points in s-levels

    *H* : arraylike
      Bottom depths [meter, positive]

    *Hc* : scalar
       Critical depth

    *cs_r* : 1D array
       s-level stretching curve

    *stagger* : [ 'rho' | 'w' ]

    *Vtransform* : [ 1 | 2 ]
       defines the transform used, defaults 1 = Song-Haidvogel

    Returns an array with ndim = H.ndim + 1 and
    shape = cs_r.shape + H.shape with the depths of the
    mid-points in the s-levels.

    Typical usage::
    
    >>> fid = Dataset(roms_file)
    >>> H = fid.variables['h'][:,:]
    >>> C = fid.variables['Cs_r'][:]
    >>> Hc = fid.variables['hc'].getValue()
    >>> z_rho = sdepth(H, Hc, C)

    """    
    H = np.asarray(H)              
    Hshape = H.shape      # Save the shape of H
    H = H.ravel()         # and make H 1D for easy shape maniplation
    C = np.asarray(C)
    N = len(C)
    outshape = (N,) + Hshape       # Shape of output
    if stagger == 'rho':
        S = -1.0 + (0.5+np.arange(N))/N    # Unstretched coordinates
    elif stagger == 'w':
        S = np.linspace(-1.0, 0.0, N)
    else:
        raise ValueError, "stagger must be 'rho' or 'w'"

    if Vtransform == 1:         # Default transform by Song and Haidvogel
        A = Hc * (S - C)[:,None]
        B = np.outer(C, H)
        return (A + B).reshape(outshape)

    elif Vtransform == 2:       # New transform by Shchepetkin
        N = Hc*S[:,None] + np.outer(C, H)
        D = (1.0 + Hc/H)
        return (N/D).reshape(outshape)

    else:
        raise ValueError, "Unknown Vtransform"

# -----------------------------

# Returnere I, J, p, q også??
# Disse fort å finne uansett

def Z2S(z_rho, X, Y, Z):
    """
    Find s-levels K and A such that
    i)  -Z < z_rho[0], 
             K=1,   A=1
    ii) z_rho[k-1] <= -Z < z_rho[k], k = 1, ..., kmax-1
             K=k,   A=(z_rho[k] + Z)/(z_rho[k]-z_rho[k-1])
    iii) z_rho[kmax-1] <= -Z, 
             K=kmax-1, A=0

    Find integer array K and real array A s.th.
    z_rho[0] < -Z <= z_rho[kmax-1]:
       -Z = A*z_rho[K-1] + (1-A)*z_rho[K]
    extend boundary values:
       -Z <= z_rho[0] : K = 1, A = 1
       -Z > z_rho[kmax-1] : K = kmax-1, A = 0

    """
    
    kmax, jmax, imax = z_rho.shape
    pmax = Z.shape

    # Find rho-based horizontal grid cell
    I = np.around(X).astype('int')
    J = np.around(Y).astype('int')

    # Find integer array K such that 
    #   z_rho[K[p]-1, J[p], I[p]] < -Z[p] <= z_rho[K[p], J[p], I[p]]
    K = np.sum(z_rho[:,J,I] < -Z, axis=0)
    K = K.clip(1, kmax-1)
    A = (z_rho[K, J, I] + Z) / (z_rho[K, J, I] - z_rho[K-1, J, I])
    A = A.clip(0, 1)

    return I, J, K, A


# --------

def sample3D(F, X, Y, K, A):
    """

    F = 3D field
    S = depth structure matrix 
    X, Y = Horizontal grid coordinates
    Z = Depth [m, positive downwards]

    Everything in rho-points

    F.shape = S.shape = (kmax, jmax, imax)
    S.shape = (kmax, jmax, imax)
    X.shape = Y.shape = Z.shape = (pmax,)

        # Hvordan gjøre dette?
    # Alle partikler samme dyp => kan interpolere et 2D felt i dette dypet
    # og deretter interpolere i dette planet
    #
    # Alternativt: 
    # 1) Finne s-verdi for alle punkter
    # 2) Interpolere (tri)-lineært i XYs-systemet,
    # Gjøre dette vektorielt, eller gå til cython/fortran med en gang
    # (løkke vil bli veldig treigt i python)

    """
    
    

    pass




