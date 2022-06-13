
def ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

def intersect(a, b, c, d):
    return ccw(a, c, d) != ccw(b, c, d) and ccw(a, b, c) != ccw(a, b, d)
    
def distance(p1, p2):
    return pow(pow(p2[0] - p1[0], 2) + pow(p2[1] - p1[1], 2), 0.5)

def segment(points, step=3):
    dashed_points = []
    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        x0, y0 = p0
        x1, y1 = p1
        
        if y0 == y1:
            y = y0
            if x0 > x1:
                s = -step
            else:
                s = step
            for x in range(x0, x1, s):
                dashed_points.append((x, y))
        elif x0 == x1:
            x = x0
            if y0 > y1:
                s = -step
            else:
                s = step
            for y in range(y0, y1, s):
                dashed_points.append((x, y))
    return dashed_points