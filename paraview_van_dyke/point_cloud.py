#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

# --- Parameters ---
R = 0.501 # radius of cylinder
sf = 100.0   #scale factor R = 0.005 sf = 10000.0 
k = 0.6  # parameter for increasing point concentration

n1 = int(k * 12000)
P1 = np.zeros((n1+1, 3))
P1[0, :] = [1, 2, 3]  # first row description for ParaView

# Generate random integers (low inclusive, high exclusive in Python, hence +1)
X1 = np.random.randint(-1000, 1001, n1)    # 7200 random x-coordinates between 300 and 1200
X1 = X1 / sf                               # dividing by 1e04 to scale coordinates
Y1 = np.random.randint(-500, 501, n1)      # 7200 random x-coordinates between 800 and 1200
Y1 = Y1 / sf                               # dividing by 1e04 to scale coordinates

P1[1:, 0] = X1                             # adding x-coordinates to P matrix (skipping header)
P1[1:, 1] = Y1                             # adding y-coordinated to P matrix

# %% Fine point cloud behind cylinder
n2 = int(k * 10000)
P2 = np.zeros((n2+1, 3))
P2[0, :] = [1, 2, 3]

X2 = np.random.randint(-500, 501, n2)
X2 = X2 / sf
Y2 = np.random.randint(-500, 501, n2)
Y2 = Y2 / sf

P2[1:, 0] = X2
P2[1:, 1] = Y2

# --- Points around cylinder (back half) ---
n = 180
angles = np.linspace(0.5 * np.pi, 1.5 * np.pi, n)
radius = R
xCenter = 0
yCenter = 0

X3 = -radius * np.cos(angles) + xCenter
Y3 = -radius * np.sin(angles) + yCenter

P3 = np.zeros((n+1, 3))
P3[0, :] = [1, 2, 3]
P3[1:, 0] = X3
P3[1:, 1] = Y3

P3.shape

# --- Combine all points ---
P = np.vstack([P1, P2[1:, :], P3[1:, :]])

# Save to CSV
# fmt='%g' uses general format (scientific notation if needed, similar to MATLAB default)
np.savetxt('P_Final_txt.csv', P, delimiter=',', fmt='%g')

print("File 'P_Final_txt.csv' generated successfully.")

# --- Save to CSV ---
P = np.delete(P, 0, axis=0)
df = pd.DataFrame(P, columns=['X', 'Y', 'Z'])
df.to_csv('P_Final_pandas.csv', index=False)

print(f"Saved {P.shape[0]} points to P_Final_pandas.csv")




# In[ ]:




