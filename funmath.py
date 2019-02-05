import numpy as np
import matplotlib.pyplot as plt

x = np.arange(-30, 30,0.05)
y = x**2 + 20*np.sin(x)
fig, ax = plt.subplots()
ax. plot(x,y)
plt.show()
