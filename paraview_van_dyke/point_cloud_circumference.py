#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

# --- Parameters ---
R = 0.505 # radius of cylinder
sf = 100.0   #scale factor R = 0.005 sf = 10000.0 
k = 0.6  # parameter for increasing point concentration



# --- Points around cylinder (back half) ---
n = 720
angles = np.linspace(0., 2. * np.pi, n)
radius = R
xCenter = 0
yCenter = 0

X = -radius * np.cos(angles) + xCenter
Y = -radius * np.sin(angles) + yCenter

P = np.zeros((n+1, 3))
P[0, :] = [1, 2, 3]
P[1:, 0] = X
P[1:, 1] = Y





# Save to CSV
# fmt='%g' uses general format (scientific notation if needed, similar to MATLAB default)
np.savetxt('circumference_txt.csv', P, delimiter=',', fmt='%g')

print("File 'circumference_txt.csv' generated successfully.")

# --- Save to CSV ---
P = np.delete(P, 0, axis=0)
df = pd.DataFrame(P, columns=['X', 'Y', 'Z'])
df.to_csv('circumference_pandas.csv', index=False)

print(f"Saved {P.shape[0]} points to P_Final_pandas.csv")









