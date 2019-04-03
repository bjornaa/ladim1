# Make the "eco"-system figure in the documentation

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def cos(a):
    return np.cos(a * np.pi / 180.0)


def sin(a):
    return np.sin(a * np.pi / 180.0)


# Wave data
T = np.linspace(0, 12, 201)
Y = -0.2 * np.abs(np.sin(2 * T))
Tpluss = np.concatenate((T, [T[-1], T[0], T[0]]))
Ypluss = np.concatenate((Y, [-5, -5, Y[0]]))

# Ocean
plt.fill(Tpluss, Ypluss, color="cyan", alpha=0.3)
plt.plot(T, Y, color="blue")

plt.text(1, 2.5, "The LADiM\necosystem", fontsize=20, color="blue")

# Sun
x, y = 10, 3
ax = plt.gca()
ax.add_patch(
    mpatches.Circle((10, 3), radius=2, facecolor="yellow", alpha=0.8, edgecolor="grey")
)
plt.text(
    x, y, "CONFIGURATION", horizontalalignment="center", verticalalignment="center"
)
# sun rays
plt.plot(
    [x + 2.3 * cos(200), x + 6 * cos(200)],
    [y + 2.3 * sin(200), y + 6 * sin(200)],
    linewidth=5,
    color="yellow",
)
plt.plot(
    [x + 2.3 * cos(230), x + 3.5 * cos(230)],
    [y + 2.3 * sin(230), y + 3.5 * sin(230)],
    linewidth=5,
    color="yellow",
)
plt.plot(
    [x + 2.3 * cos(260), x + 2.8 * cos(260)],
    [y + 2.3 * sin(260), y + 2.8 * sin(260)],
    linewidth=5,
    color="yellow",
)
plt.plot(
    [x + 2.3 * cos(290), x + 2.8 * cos(290)],
    [y + 2.3 * sin(290), y + 2.8 * sin(290)],
    linewidth=5,
    color="yellow",
)

# Module boxes
plt.text(
    3,
    -1,
    "GRIDFORCE",
    fontsize=16,
    horizontalalignment="center",
    verticalalignment="center",
    bbox=dict(boxstyle="round4", facecolor="magenta", alpha=0.5),
)

plt.text(
    9,
    -1,
    "RELEASE",
    fontsize=16,
    horizontalalignment="center",
    verticalalignment="center",
    bbox=dict(boxstyle="round4", facecolor="magenta", alpha=0.5),
)

plt.text(
    2,
    -2.5,
    "TRACKER",
    fontsize=16,
    horizontalalignment="center",
    verticalalignment="center",
    bbox=dict(boxstyle="round4", facecolor="magenta", alpha=0.5),
)

plt.text(
    6,
    -2.5,
    "STATE",
    fontsize=16,
    horizontalalignment="center",
    verticalalignment="center",
    bbox=dict(boxstyle="round4", facecolor="magenta", alpha=0.5),
)

plt.text(
    10,
    -2.5,
    "IBM",
    fontsize=16,
    horizontalalignment="center",
    verticalalignment="center",
    bbox=dict(boxstyle="round4", facecolor="magenta", alpha=0.5),
)

plt.text(
    6,
    -4,
    "OUTPUT",
    fontsize=16,
    horizontalalignment="center",
    verticalalignment="center",
    bbox=dict(boxstyle="round4", facecolor="magenta", edgecolor="grey", alpha=0.5),
)

# Arrows
plt.arrow(4.2, -1.43, 0.7, -0.5, head_width=0.2, head_length=0.3, color="black")

plt.arrow(7.8, -1.43, -0.7, -0.5, head_width=0.2, head_length=0.3, color="black")

# Poor man's two-way arrows
plt.arrow(3.7, -2.5, 0.7, 0, head_width=0.2, head_length=0.3, color="black")
plt.arrow(4.7, -2.5, -0.7, 0, head_width=0.2, head_length=0.3, color="black")

plt.arrow(7.2, -2.5, 1.7, 0, head_width=0.2, head_length=0.3, color="black")
plt.arrow(9.2, -2.5, -1.7, 0, head_width=0.2, head_length=0.3, color="black")


plt.arrow(6, -3, 0, -0.33, head_width=0.2, head_length=0.3, color="black")

ax.axis("off")

plt.axis((0, 12, -5, 5))
plt.axis("image")
plt.show()
# plt.savefig('ladim_ecosystem.png', dpi=300, bbox_inches='tight')
