
#include <vector>
#include <tuple>
#include <map>

typedef std::pair<int, int> Point2D;
typedef std::tuple<Point2D, Point2D, Point2D> Triangle;
typedef std::map<Triangle, std::vector<Triangle>> TriangleToTrianglesMap;

TriangleToTrianglesMap triangles_intersection(std::vector<Triangle> &triangles);