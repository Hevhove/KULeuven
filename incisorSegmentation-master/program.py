import os
import fnmatch
import numpy as np
import scipy.spatial as spatial
import scipy.misc as smp
import cv2
import math
from PIL import Image,ImageDraw

def pca(X, nb_components=0):
    '''
    Do a PCA analysis on X
    @param X:                np.array containing the samples
                             shape = (nb samples, nb dimensions of each sample)
    @param nb_components:    the nb components we're interested in
    @return: return the nb_components largest eigenvalues and eigenvectors of the covariance matrix and return the average sample 
    '''
    [n,d] = X.shape
    if (nb_components <= 0) or (nb_components>n):
        nb_components = n
    
    #Calculating mean sample
    mean_vector = np.zeros((d,1))
    for i in range (d):
        mean_vector[i] = np.mean(X[:,i])

    #Calculating scatter matrix
    scatter_matrix = np.zeros((n,n))
    for i in range(n):
        scatter_matrix += ((X[i,:].reshape(d,1) - mean_vector).T).dot(X[i,:].reshape(d,1) - mean_vector)

    #Calculating eigenvalues
    eig_val, eig_vec = np.linalg.eig(scatter_matrix)

    #transform the eigenvectors to the correct vectorspace
    transformed_eig_vec = np.zeros((n,d))
    for i in range(len(eig_vec)):
        temp = 0
        for j in range(len(eig_vec[i])):
            temp += eig_vec[i][j] * X[j,:]
        transformed_eig_vec[i] = temp/np.linalg.norm(temp)

    #Sorting eigenvalues
    eig_pairs = [(np.abs(eig_val[i]), transformed_eig_vec[i,:]) for i in range(len(eig_val))]
    eig_pairs.sort(key=lambda x: x[0],reverse = True)

    #splitting the pairs up again
    eig_vals  = np.zeros((nb_components,1))
    eig_vecs  = np.zeros((nb_components,d))
    for i in range(nb_components):
        eig_vals[i] = eig_pairs[i][0]
        eig_vecs[i] = eig_pairs[i][1]
        
    return  [eig_vals,eig_vecs,mean_vector.flatten()]

def project(W, X, mu):
    '''
    Project X on the space spanned by the vectors in W.
    mu is the average image.
    '''
    dim = X.shape
    n,d = W.shape

    projection = np.zeros(dim)
    
    v = X-mu
    for i in range(n):
        projection += (W[i,:].dot(v))*W[i,:]
    
    return projection 

def reconstruct(W, Y, mu):
    '''
    Reconstruct an image based on its PCA-coefficients Y, the eigenvectors W and the average mu.
    '''
    dim = Y.shape
    n,d = W.shape
    
    reconstruct = np.zeros(dim)
    for i in range(n):
        reconstruct += Y *(W[i,:].T)

    reconstruct += mu
    
    return reconstruct 


def load_landmark(mapname,teeth,photo):
    
    filename = "./_Data/Landmarks/"  + mapname+"/landmarks"+str(photo)+"-"+str(teeth)+".txt"
    fileL = open(filename,'r')
    lines = fileL.read().splitlines()
    landmark  = np.zeros((80,1))
    for i in range(len(lines)):
        landmark[i,:] = float(lines[i])

    return landmark.reshape(40,2)

def load_landmarks():

    numberTeeth = 8;
    numberPhotos = 20
    landmarks =  np.zeros((numberTeeth,numberPhotos,40,2))
    for i in range(numberTeeth):
        for j in range(numberPhotos):
            if (j <10):
                landmarks[i,j,:,:] = load_landmark("original",i+1,j+1)
            else:
                landmarks[i,j,:,:] = load_landmark("mirrored",i+1,j+5)
    return landmarks

def load_ref_landmarks(mapname,photo):

    numberTeeth = 8;
    landmarks =  np.zeros((numberTeeth,40,2))
    for i in range(numberTeeth):
                landmarks[i,:,:] = load_landmark(mapname,i+1,photo)
            
    return landmarks

def rotateAndScale(x,y,s,theta):
    t = math.radians(theta)
    xn = (s*math.cos(t)*x)-(s*math.sin(t)*y)
    yn = (s*math.sin(t)*x)+(s*math.cos(t)*y)
    return xn,yn


def calculate_outline(landmark,centerpoint,tx,ty,s,theta):

    points = landmark.reshape((40,2))
    outline = np.zeros((40,2),dtype=np.int32)
    for i in range(40):
        px,py = rotateAndScale(points[i,0],points[i,1],s,theta)
        outline[i,0] = int(round(centerpoint[0] + px + tx))
        outline[i,1] = int(round(centerpoint[1] + py + ty))

    return outline.reshape((80))

def visualize_outline(image,landmark, color):

    shape = landmark.reshape((40,2))
    cv2.polylines(image,[shape],True,color,thickness=1)
        
    return image

def process_landmarks(landmarks):

    a,b,c,d = landmarks.shape
    landmarks_pc = np.zeros((a,b,c,d))

    for i in range(a):
        for j in range(b):
            landmarks_pc[i,j,:,:] = spatial.procrustes(landmarks[i,1,:,:],landmarks[i,j,:,:])[1]
      
    return landmarks_pc


def create_PCA(data):

    a,b,c,d = data.shape
    number_components  = 1 
    reshaped_data = data.reshape((8,20,80))
    mean_collection = np.zeros((8,80))
    eigvals_collection= np.zeros((8,number_components))
    eigvecs_collection= np.zeros((8,number_components,80))
    for i in range(a):
        eigval, eigvec, mean = pca(reshaped_data[i,:,:],number_components)
        mean_collection[i,:] = mean
        eigvals_collection[i,:] = eigval.flatten()
        eigvecs_collection[i,:,:] = eigvec
        
    return mean_collection,eigvals_collection,eigvecs_collection

def load_image(number):

    im= Image.open("./_Data/Radiographs/" + number +  ".tif")

    imarray = np.array(im)

    return imarray

def smooth(image):

    median = cv2.medianBlur(image,5)
    blur = cv2.bilateralFilter(median,9,75,75)

    return blur

def filter_image_scharr(image,threshold):

    x,y,c = image.shape    
    scharrx = cv2.Sobel(image,-1,1,0,ksize=-1)
    scharry = cv2.Sobel(image,-1,0,1,ksize=-1)
    scharr = np.zeros((x,y,c))

    for i in range(x):
        for j in range(y):
            for k in range(c):
                scharr[i,j,k] = math.sqrt(math.pow(scharrx[i,j,k],2) + math.pow(scharry[i,j,k],2))
              
    scharr = scharr / np.amax(scharr)*255

    for i in range(x):
        for j in range(y):
            for k in range(c):
                if scharr[i,j,k] < threshold:
                    scharr[i,j,k] = 0
    
    return scharr

def filter_image_sobel(image,threshold):

    x,y,c = image.shape
    sobelx = cv2.Sobel(image,-1,1,0,ksize=3)
    sobely = cv2.Sobel(image,-1,0,1,ksize=3)
    sobel = np.zeros((x,y,c))

    for i in range(x):
        for j in range(y):
            for k in range(c):
                sobel[i,j,k] = math.sqrt(math.pow(sobelx[i,j,k],2) + math.pow(sobely[i,j,k],2))

    sobel = sobel / np.amax(sobel)*255

    for i in range(x):
        for j in range(y):
            for k in range(c):
                if sobel[i,j,k] < threshold:
                    sobel[i,j,k] = 0

    return sobel

def filter_image_sobel2(image,threshold):

    x,y,c = image.shape
    sobelx = cv2.Sobel(image,-1,1,0,ksize=5)
    sobely = cv2.Sobel(image,-1,0,1,ksize=5)
    sobel = np.zeros((x,y,c))

    for i in range(x):
        for j in range(y):
            for k in range(c):
                sobel[i,j,k] = math.sqrt(math.pow(sobelx[i,j,k],2) + math.pow(sobely[i,j,k],2))

    sobel = sobel / np.amax(sobel)*255

    for i in range(x):
        for j in range(y):
            for k in range(c):
                if sobel[i,j,k] < threshold:
                    sobel[i,j,k] = 0

    return sobel
    

def calculate_normal(Pl,Pr):

    dx = Pr[0]-Pl[0]
    dy = Pr[1]-Pl[1]

    n1 = np.array([-dy,dx])
    return n1/np.linalg.norm(n1)

def find_best_position_point(image,point,normal,search_radius):

    height,width,_ = image.shape
    best_loc = point
    px = min(point[0],width-1)
    py = min(point[1],height-1)
    best_val = image[py,px,0]
    for i in range(-(search_radius-1),search_radius):
        offset = np.multiply(i,normal)
        newpoint  = point + offset
        x,y = newpoint.astype(int)
        px = min(x,width-1)
        py = min(y,height-1)
        pixval = image[py,px,0]
        if(pixval > best_val):
            best_val = pixval
            best_loc = newpoint

    final_loc = (best_val/255)*best_loc + (1-best_val/255)*point
    
    return best_loc

def find_best_position(image,outline,search_radius):
    points_old = outline.reshape((40,2))
    new_best_position = np.zeros((40,2))
    for i in range(40):
        point = points_old[i,:]
        normal = calculate_normal(points_old[i-1],points_old[(i+1)%40])
        new_best_position[i,:] = find_best_position_point(image,point,normal,search_radius)
        
    return new_best_position.reshape((80))

def get_scale_rotation(ax,ay):

    theta = math.atan(ay/ax)
    s = ax/math.cos(theta)
    return s , math.degrees(theta)

def align_model(outline_old,outline_new):
    points_old = outline_old.reshape((40,2))
    points_new = outline_new.reshape((40,2))
    X1,Y1 = np.sum(points_new,axis=0)
    X2,Y2 = np.sum(points_old,axis=0)
    W = 40
    Z = 0
    C1=0
    C2=0
    for i in range(40):
        Z += points_old[i,0]**2 + points_old[i,1]**2
        C1 += points_new[i,0]*points_old[i,0] + points_new[i,1]*points_old[i,1]
        C2 += points_new[i,1]*points_old[i,0] - points_new[i,0]*points_old[i,1]
    

    A = np.array([[X2,-Y2,W,0],
                  [Y2,X2,0,W],
                  [Z,0,X2,Y2],
                  [0,Z,-Y2,X2]])
    B = np.array([ X1,Y1,C1,C2])

    X,_,_,_ = np.linalg.lstsq(A,B)
    s,theta = get_scale_rotation(X[0],X[1])
    return X[2],X[3],(s-1),theta,

def deform_model(outline_old,outline_new,P,dtx,dty,theta,dtheta,s,ds):
    
    diff  = (outline_new-outline_old).reshape((40,2))
    points_old = outline_old.reshape((40,2))
    points_new = outline_new.reshape((40,2))

    dx = np.zeros((40,2))

    for i in range(40):
        y = rotateAndScale(points_old[i,0],points_old[i,1],s,theta) + diff[i,:] - [dtx,dty]
        dx[i,:] = rotateAndScale(y[0],y[1],1/(s*(1+ds)),-(theta+dtheta)) - points_old[i,:]

    
    dx = dx.reshape((80,1))
    db = np.dot(P,dx)
    return db

def in_image(outline, width, height):
    points = outline.reshape((40,2))
    ymin,xmin = np.amin(points,axis = 0)
    ymax,xmax = np.amax(points,axis = 0)
    if(xmin < 0 or ymin <0):
        return False
    if(xmax >= width):
        return False
    if(ymax >= height):
        return False

    return True

def find_outline_tooth(image, landmark,P,lambdas, centerpoint,wtx,wty,ws,wtheta,search_radius):

    height,width,_ = image.shape
    
    i=0
    stop = 100

    wb = np.diag(np.sqrt(lambdas))
    tx =0
    ty=0
    s = 580

    theta=0
    b = np.zeros((1))

    Dmax = 800
    
    while (i<stop):
        current_outline = calculate_outline(landmark,centerpoint,tx,ty,s,theta) + (np.dot(b,P).astype(int))
        
        new_outline = find_best_position(image,current_outline,search_radius)
        dtx,dty,ds,dtheta = align_model(current_outline,new_outline)
        db = deform_model(current_outline,new_outline,P,dtx,dty,theta,dtheta,s,ds)

        tx = tx + wtx*dtx
        ty = ty + wty*dty
        s = s* (1+ (ws * ds))
        theta = theta +  wtheta * dtheta
        
        b = b+ np.dot(db,wb)

        
        
        if(  np.linalg.norm(b) > 30 *  math.sqrt(np.linalg.norm(lambdas)) and ((b[0])**2)/lambdas[0] > Dmax):
            b = b * (Dmax/(((b[0])**2)/lambdas[0]))

        if(((b[0])**2)/lambdas[0] > Dmax):
            break

        i += 1

        
    final_outline = calculate_outline(landmark,centerpoint,tx,ty,s,theta)
    final_outline = final_outline + (np.dot(b,P).astype(int))

    return final_outline

def root_mean_squared_error(ref,data):

    x = ref.shape[0]
    error_sum = 0

    for i in range(x):
        error_sum += (ref[i] - data[i])**2

    error_sum = error_sum / x

    return math.sqrt(error_sum)
                       
if __name__ == '__main__':

    landmarks_raw = load_landmarks()

# only work with non mirrored picture because of the negative nature of the mirrored x values
# maybe extend this to work with all
    landmarks_mean = np.mean(landmarks_raw[:,:10,:,:],axis=(1,2))
 
    landmarks_processed = process_landmarks(landmarks_raw)

    means, eigvals, eigvecs = create_PCA(landmarks_processed)
  
    
    
    ref_landmarks = load_ref_landmarks("original",11)
    im = load_image('11')
    im = smooth(im)

    image1 = filter_image_scharr(im,33)
    img1 = image1

    
    centers_11 = np.array([[1305,820],
                            [1400,826],
                            [1520,823],
                            [1618,815],
                            [1360,1125],
                            [1445,1125],
                            [1520,1125],
                            [1595,1125]])

    centers_13 = np.array([[1390,735],
                            [1470,746],
                            [1560,743],
                            [1650,740],
                            [1405,1050],
                            [1475,1050],
                            [1540,1050],
                            [1600,1050]])
       
    new_centers = centers_11;
     
    search_radius = 10
    wtx = 0.04
    wty = 0.12
    ws = 0.6
    wtheta = 1

    img2 = im.copy()
    error =  0
    for i in range(8):   
        outline = find_outline_tooth(image1, means[i,:],eigvecs[i,:,:],eigvals[i,:],new_centers[i,:],wtx,wty,ws,wtheta,search_radius)
        error += root_mean_squared_error(ref_landmarks[i,:,:].flatten(),outline.flatten())
        img2 = visualize_outline(img2, (ref_landmarks[i,:,:].reshape((1,80)).astype(int)), (128,0,0))
        img2 = visualize_outline(img2, outline,(0,128,0))
    error /= 8   

    cv2.imwrite('Output.tif',img2)
    print "Average RMSE error on all the teeth: " + str(error)


