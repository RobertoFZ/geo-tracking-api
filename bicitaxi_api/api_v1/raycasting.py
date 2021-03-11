from collections import namedtuple
import sys

class Raycasting():
    Pt = namedtuple('Pt', 'x, y')  # Point
    Edge = namedtuple('Edge', 'a, b')  # Polygon edge from a to b
    Poly = namedtuple('Poly', 'name, edges')  # Polygon

    _eps = 0.00001
    _huge = sys.float_info.max
    _tiny = sys.float_info.min

    polygon = None
    point = None

    def __init__(self, polygon_points, register_point):
        # Process to create objects using the params
        point = register_point.split(",")
        point_to_check = self.Pt(x=point[0], y=point[1])

        # Polygon creation
        # Create the edges objects
        edges = []
        last_point = None
        for polygon_point in polygon_points:
            polygon_point = polygon_point.split(",")
            print(polygon_point)
            if last_point:
                edge = None
                if len(last_point) == 3 and len(polygon_point) == 3:
                    edge = self.Edge(a=self.Pt(x=last_point[1], y=last_point[2]),
                                     b=self.Pt(x=polygon_point[1], y=polygon_point[2]))
                if len(last_point) == 3 and len(polygon_point) == 2:
                    edge = self.Edge(a=self.Pt(x=last_point[1], y=last_point[2]),
                                     b=self.Pt(x=polygon_point[0], y=polygon_point[1]))
                if len(last_point) == 2 and len(polygon_point) == 3:
                    edge = self.Edge(a=self.Pt(x=last_point[0], y=last_point[1]),
                                     b=self.Pt(x=polygon_point[1], y=polygon_point[2]))
                if len(last_point) == 2 and len(polygon_point) == 2:
                    edge = self.Edge(a=self.Pt(x=last_point[0], y=last_point[1]),
                                     b=self.Pt(x=polygon_point[0], y=polygon_point[1]))
                edges.append(edge)
            last_point = polygon_point

        self.polygon = self.Poly(name='poly', edges=edges)
        self.point = point_to_check

    def rayintersectseg(self, p, edge):
        '''
        Takes a point p=Pt() and an edge of two endpoints a,b=Pt() of a line segment returns boolean
        :param p: point to intersect
        :param edge: polygon edge
        :return: if the point intersect polygon edge
        '''
        a, b = edge
        if a.y > b.y:
            a, b = b, a
        if p.y == a.y or p.y == b.y:
            p = self.Pt(p.x, p.y + self._eps)

        intersect = False

        if (p.y > b.y or p.y < a.y) or (
                p.x > max(a.x, b.x)):
            return False

        if p.x < min(a.x, b.x):
            intersect = True
        else:
            if abs(a.x - b.x) > self._tiny:
                m_red = (b.y - a.y) / float(b.x - a.x)
            else:
                m_red = self._huge
            if abs(a.x - p.x) > self._tiny:
                m_blue = (p.y - a.y) / float(p.x - a.x)
            else:
                m_blue = self._huge
            intersect = m_blue >= m_red
        return intersect

    def _odd(self, x):
        return x % 2 == 1

    def ispointinside(self):
        '''
        Function to check if point is inside a polygon
        :return:
        '''
        ln = len(self.polygon)
        return self._odd(sum(self.rayintersectseg(self.point, edge)
                             for edge in self.polygon.edges))

    def polypp(self):
        '''
        Print the polygon name and edges
        :return:
        '''
        print("\n  Polygon(name='%s', edges=(" % self.polygon.name)
        print('   ', ',\n    '.join(str(e)
                                    for e in self.polygon.edges) + '\n    ))')
