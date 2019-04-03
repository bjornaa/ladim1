# Particle release for the LADiM logo

import numpy as np

N = 10000  # Number of particles per segment

# Shorthand
conc = np.concatenate
lsp = np.linspace

# Make the letters
LX = conc((lsp(0, 0, N), lsp(0, 0.85, N)))
LY = conc((lsp(1.7, 0, N), lsp(0, 0, N)))

AX = 0.95 + conc((lsp(0, 0.6, N), lsp(0.6, 1.2, N), lsp(0.27, 0.93, N)))
AY = conc((lsp(0, 1.7, N), lsp(1.7, 0, N), lsp(0.765, 0.7645, N)))

T = np.linspace(-np.pi / 2, np.pi / 2, N)
DX = 2.25 + conc((0.85 * np.cos(T), lsp(0, 0, N)))
DY = conc((0.85 * (1 + np.sin(T)), lsp(1.7, 0, N)))

IX = 3.35 + conc((lsp(0, 0, N), lsp(0, 0, N)))
IY = conc((lsp(0, 1.7, N), lsp(1.9, 1.9, N)))

MX = 3.65 + conc((lsp(0, 0, N), lsp(0, 0.7, N), lsp(0.7, 1.4, N), lsp(1.4, 1.4, N)))
MY = conc((lsp(0, 1.7, N), lsp(1.7, 0.765, N), lsp(0.765, 1.7, N), lsp(1.7, 0, N)))

# Scale and position the release
X = conc((LX, AX, DX, IX, MX))
Y = conc((LY, AY, DY, IY, MY))

X = 95 + 6 * X
Y = 110 + 6 * Y

Z = 5

with open("logo.rls", mode="w") as f:
    for (x, y) in zip(X, Y):
        f.write("1 1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n".format(x, y, Z))
