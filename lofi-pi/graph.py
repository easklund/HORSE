import time
import matplotlib.pyplot as plt

#%matplotlib notebook

fig = plt.figure()
ax = fig.add_subplot(111)
fig.show()

i = 0
x, y = [], []
while True:
	x.append(i)
	y.append(i*i+3)

	ax.plot(x, y, color='b')

	fig.canvas.draw()

	ax.set_xlim(left=max(0, i-50), right=i+50)

	time.sleep(0.1)
	i += 1
