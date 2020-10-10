import numpy as np
import cv2
from matplotlib import pyplot as plt
import math


img = cv2.imread('capture_mire_0.png',0)
img2 = cv2.imread('capture_mire_1.png',0)

# print(cv2.findChessboardCorners(img, (7, 7)))
found, coord_px = cv2.findChessboardCorners(img, (7, 7), None)
found, coord_px2 = cv2.findChessboardCorners(img2, (7, 7), None)
cv2.drawChessboardCorners(img, (7,7), coord_px, found)
cv2.drawChessboardCorners(img2, (7,7), coord_px2, found)
#de haut en bas de gauche à droite

#Coordonnées des coins sur l'image en réalité (coordonnées objet de la mire)
coord_mm = [[[20*i, 20*j] for i in range(7)] for j in range(7)]
coord_mm = np.reshape(coord_mm, np.shape(coord_px))

zToUse = 0
zToUse2 = 120
i2, i1 = np.shape(img)

i1 = i1/2
i2 = i2/2

# mem = np.copy(coord_px[:,0,1])
# coord_px[:,0,1] = coord_px[:,0,0]
# coord_px[:,0,0] = mem

# mem2 = np.copy(coord_px2[:,0,1])
# coord_px2[:,0,1] = coord_px2[:,0,0]
# coord_px2[:,0,0] = mem2

sgnO2c =(i2 > coord_px[0,0,1]) * (-1) + (i2 < coord_px[0,0,1]) * 1
coord_px = np.array(coord_px)
coord_px2 = np.array(coord_px2)

U1 = np.concatenate((coord_px[:,:,0], coord_px2[:,:,0]), axis = 0) - i1
U2 = np.concatenate((coord_px[:,:,1], coord_px2[:,:,1]), axis = 0) - i2

U = [[U2[i][0]]*4 + [-U1[i][0]]*3 for i in range(len(U1))]
x0 = [coord_mm[i,0,:].tolist() + [zToUse, 1] + coord_mm[i,0,:].tolist() + [zToUse] for i in range(np.shape(coord_px)[0])]
x0 += [coord_mm[i,0,:].tolist() + [zToUse2, 1] + coord_mm[i,0,:].tolist() + [zToUse2] for i in range(np.shape(coord_px2)[0])]

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

r31=r3[0]
r32=r3[1]
r33=r3[2]

phi=-math.atan(r23/r33)
gamma=-math.atan(r12/r11)
omega=math.atan(r13/(-r23*math.sin(phi)+r33*math.cos(phi)))

print("beta",beta,"angles phi,gamma,omega",np.array([phi, gamma, omega])*180/math.pi)

x0bis = np.array([coord_mm[i,0,:].tolist() + [zToUse] for i in range(np.shape(coord_px)[0])]).T
x0bis = np.concatenate((x0bis,np.array([coord_mm[i,0,:].tolist() + [zToUse2] for i in range(np.shape(coord_px2)[0])]).T), axis = 1)
vecR2 = np.reshape(-(np.dot(r2, x0bis)+o2c), np.shape(U2))

B = np.concatenate([U2, vecR2], axis = 1) #ok


vecR3 = np.reshape((np.dot(r3, x0bis)), np.shape(U2))

R = np.multiply(vecR3, -U2) #multiply ok

r31=r3[0]
r32=r3[1]
r33=r3[2]


B_inv = np.linalg.pinv(B)
M = np.dot(B_inv, R)


f = 4
o3c = M[0]
f2 = M[1]

s2 = f/f2
s1 = s2/beta

print("f",f)
print("s1",s1,"s2",s2)

f1=f/s1


# print(np.shape(x0bis))
# reproduced_U1_array = np.array([ [f1*(r11*x0bis[0][i]+r12*x0bis[1][i]+r13*x0bis[2][i]+o1c)/(r31*x0bis[0][i]+r32*x0bis[1][i]+r33*x0bis[2][i]+o3c) + i1] for i in range(np.shape(x0bis)[1])])
# reproduced_U2_array = np.array([ f1*(r11*x0bis[0][i]+r12*x0bis[1][i]+r13*x0bis[2][i]+o1c)/(r31*x0bis[0][i]+r32*x0bis[1][i]+r33*x0bis[2][i]+o3c) + i2 for i in range(np.shape(x0bis)[1])])

thickness = 3
radius = 5
color = (255, 0, 0)
for loop in range(np.shape(x0bis)[1]) :

    reproduced_U11 = f1*(r11*x0bis[0][loop]+r12*x0bis[1][loop]+r13*x0bis[2][loop]+o1c)/(r31*x0bis[0][loop]+r32*x0bis[1][loop]+r33*x0bis[2][loop]+o3c) + i1 
    reproduced_U22 = f2*(r21*x0bis[0][loop]+r22*x0bis[1][loop]+r23*x0bis[2][loop]+o2c)/(r31*x0bis[0][loop]+r32*x0bis[1][loop]+r33*x0bis[2][loop]+o3c) + i2 
    center_coordinates = (int(reproduced_U11), int(reproduced_U22))
    if loop < np.shape(x0bis)[1]/2:
        cv2.circle(img, center_coordinates, radius, color, thickness)
    else :
        cv2.circle(img2, center_coordinates, radius, color, thickness)


cv2.imshow('image 1', img) #affichage
cv2.imshow('image 2', img2) #affichage

cv2.waitKey(0)
cv2.destroyAllWindows()









