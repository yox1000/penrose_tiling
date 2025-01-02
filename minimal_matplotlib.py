import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg instead of Qt5Agg
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([0, 1, 2], [0, 1, 0])
plt.show(block=True)
