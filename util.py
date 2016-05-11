import math

def dist(a,b):
    return math.sqrt((a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1]))


def average_distance(positions):
    distances = []
    for i in range(len(positions)-1):
        for j in range(i+1, len(positions)):
            distances.append(dist(positions[i], positions[j]))

    
