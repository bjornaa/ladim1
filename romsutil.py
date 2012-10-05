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

def Z2S(z_rho, X, Y, Z):
    """
    Find s-levels C s.th.
    z_rho[C[p]] <= -Z < z_rho[C[p]+1]
    """
    
    kmax, jmax, imax = z_rho.shape
    pmax = Z.shape

    # Find rho-based horizontal grid cell
    I = np.around(X).astype('int')
    J = np.around(Y).astype('int')

    print "I = ", I
    print "J = ", J

    # Find integer array K such that 
    #   z_rho[K[p]-1, J[p], I[p]] < -Z[p] <= z_rho[K[p], J[p], I[p]]
    print z_rho[0, J, I]
    K = np.sum(z_rho[:,J,I] < -Z, axis=0)
    print K
    print z_rho[K-1,J,I], -Z, z_rho[K,J,I]
    K.clip(1, kmax)
    print


    # Find integer array C, shape = (pmax,) s.th.
    # z_rho[C[p]-1] < -Z <= z_rho[C[p]]
    #C = np.sum(z_rho < -Z, axis=0)
    #C = clip(1, 


# --------

def sample3D(F, X, Y, S):
    """

    F = 3D field
    S = depth structure matrix 
    X, Y = Horizontal grid coordinates
    Z = Depth [m, positive downwards]

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




