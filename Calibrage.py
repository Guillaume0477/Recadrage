import numpy as np
import cv2
from matplotlib import pyplot as plt
import math


img = cv2.imread('capture_mire_0.png',0)

# print(cv2.findChessboardCorners(img, (7, 7)))
found, coord_px = cv2.findChessboardCorners(img, (7, 7), None)
cv2.drawChessboardCorners(img, (7,7), coord_px, found)
#de haut en bas de gauche à droite

#Coordonnées des coins sur l'image en réalité (coordonnées objet de la mire)
coord_mm = [[[20*i, 20*j] for j in range(7)] for i in range(7)]
coord_mm = np.reshape(coord_mm, np.shape(coord_px))

zToUse = 0
i1, i2 = np.shape(img)
print(np.shape(img))
i1 /= 2
i2 /= 2

mem = np.copy(coord_px[:,0,1])
coord_px[:,0,1] = coord_px[:,0,0]
coord_px[:,0,0] = mem

sgnO2c = (i2 > coord_px[0,0,1]) * (-1) + (i2 < coord_px[0,0,1]) * 1
coord_px = np.array(coord_px)

U1 = coord_px[:,:,0] - i1
U2 = coord_px[:,:,1] - i2



U = [[coord_px[i,0,1] - i2]*4 + [-coord_px[i,0,0]+i1]*3 for i in range(len(U1))]
x0 = [coord_mm[i,0,:].tolist() + [zToUse, 1] + coord_mm[i,0,:].tolist() + [zToUse] for i in range(len(U1))]


#Multiplication de Hadamard
A = np.multiply(U,x0)
A_inv = np.linalg.pinv(A)

l=np.dot(A_inv,U1)
l=l.T
l=l[0]


modo2c=1/math.sqrt(l[4]**2+l[5]**2+l[6]**2)
beta=modo2c*math.sqrt(l[0]**2+l[1]**2+l[2]**2)
o2c = sgnO2c * modo2c
o1c=l[3]*o2c/beta
r11=l[0]*o2c/beta
r12=l[1]*o2c/beta
r13=l[2]*o2c/beta
r21=l[4]*o2c
r22=l[5]*o2c
r23=l[6]*o2c

r1 = np.array([r11,r12,r13])
r2 = np.array([r21,r22,r23])
r3 = np.cross(r1,r2)
print(r1, r2, r3)
r31=r3[0]
r32=r3[1]
r33=r3[2]

phi=-math.atan(r23/r33)
gamma=-math.atan(r12/r11)
omega=math.atan(r13/(-r23*math.sin(phi)+r33*math.cos(phi)))

print([phi, gamma, omega])

x0bis = np.array([coord_mm[i,0,:].tolist() + [zToUse] for i in range(len(U2))]).T
vecR2 = -(np.dot(r2, x0bis))

# B = [U2, vecR2]

# print(np.shape(B))

# img[434:438,438:560] = 0
# cv2.imshow('Capture_Affine', img) #affichage

# cv2.waitKey(0)
# cv2.destroyAllWindows()









