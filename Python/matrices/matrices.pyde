
xmin = -10
xmax = 10

ymin = -10
ymax = 10

rangex = xmax - xmin
rangey = ymax - ymin

rotation_matrix = [[0,-1],[1,0]]
reflectionm_matrix = [[1,0],[0,-1]]
matrix1 = [[-1,1],[1,1]]
matrix2 = [[0,-1],[-1,0]]

def multmatrix(a, b):
    # Returns product of matrix a and b
    m = len(a) # Number of rows in first matrix
    n = len(b[0]) # Number of columns in second matrix
    
    newmatrix = []
    for i in range(m):
        row = []
        for j in range(n): # for every column in b
            sum1 = 0
            for k in range(len(b)):
                sum1 += a[i][k]*b[k][j] # !=> (i x j) X (j x k) = i x k
            row.append(sum1)
        newmatrix.append(row)
    return newmatrix

def transpose(a):
    output = []
    m = len(a)
    n = len(a[0])
    
    for i in range(n):
        output.append([])
        for j in range(m):
            output[i].append(a[j][i])
    
    return output

def setup():
    global xscl, yscl
    size(600,600)
    xscl = width/rangex
    yscl = -height/rangey
    noFill()
    
def draw():
    global xscl, yscls
    background(0)
    translate(width/2, height/2)
#    grid(xscl, yscl)
#    ang = map(mouseX,0,width,0,TWO_PI)
#    rot_matrix = [[cos(ang),-sin(ang)],[sin(ang),cos(ang)]]
    rot = map(mouseX, 0, width, 0, TWO_PI)
    tilt = map(mouseY, 0, height, 0, TWO_PI)
#    newmatrix = transpose(multmatrix(rot_matrix, transpose(fmatrix)))
    newmatrix = transpose(multmatrix(rottilt(rot,tilt), transpose(fmatrix_3d)))
    strokeWeight(2)
#    graphPoints(fmatrix)
    stroke(255,0,0)
    graphPoints(newmatrix,edges)
#    graphPoints(newmatrix)
    
fmatrix = [[0,0],[1,0],[1,2],[2,2],[2,3],[1,3],[1,4],[3,4],[3,5],[0,5]]
fmatrix_3d = [[0,0,0],[1,0,0],[1,2,0],[2,2,0],[2,3,0],[1,3,0],[1,4,0],[3,4,0],[3,5,0],[0,5,0],[0,0,1],[1,0,1],[1,2,1],[2,2,1],[2,3,1],[1,3,1],[1,4,1],[3,4,1],[3,5,1],[0,5,1]]
# The edges variable links the two edges of the "back" part of F and the "front" part. 
# Example: First entry draws an edge from point 0 (0,0,0) to point 1 (1,0,0) by [0,1].
edges = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,0],[10,11],[11,12],[12,13],[13,14],[14,15],[15,16],[16,17],[17,18],[18,19],[19,10],[0,10],[1,11],[2,12],[3,13],[4,14],[5,15],
         [6,16],[7,17],[8,18],[9,19]]
# The first 10 edges draw the "front" F and the next 10 edges draw the "rear" F, with 10 more edges between the front and rear...
# Example: edge [0,10] draws a segment between point 0 (0,0,0) and point 10 (0,0,1)!

def rottilt(rot, tilt):
    rotmatrix_Y = [[cos(rot),0,sin(rot)],[0,1,0],[-sin(rot),0,cos(rot)]]
    rotmatrix_X = [[1,0,0],[0,cos(tilt),sin(tilt)],[0,-sin(tilt),cos(tilt)]]
    return multmatrix(rotmatrix_Y, rotmatrix_X)

'''def graphPoints(matrix):
    beginShape()
    for pt in matrix:
        vertex(pt[0]*xscl, pt[1]*yscl)
    endShape(CLOSE)'''
    
def graphPoints(pointsList, edges):
    for e in edges:
        line(pointsList[e[0]][0]*xscl, pointsList[e[0]][1]*yscl, pointsList[e[1]][0]*xscl, pointsList[e[1]][1]*yscl)
        
# Drawing a line between points like this: line(x1, y1, x2, y2).    
def grid(xscl, yscl):
    strokeWeight(1)
    stroke(0, 255, 255)
    for i in range(xmin, xmax+1):
        line(i*xscl, ymin*yscl, i*xscl, ymax*yscl)
    for i in range(ymin, ymax+1):
        line(xmin*xscl, i*yscl, xmax*xscl, i*yscl)
    stroke(0)
    line(0, ymin*yscl, 0, ymax*yscl)
    line(xmin*xscl, 0, xmax*xscl, 0)
