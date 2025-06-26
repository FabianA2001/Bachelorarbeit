
#include <vector>
#include <tuple>
#include <map>

typedef std::pair<int, int> Point;
typedef std::tuple<Point, Point, Point> Triangle_as_Point;
typedef std::tuple<int,int,int> Triangle_as_Node;
typedef std::map<Triangle_as_Node, std::vector<Triangle_as_Node>> TriangleToTrianglesMap;

TriangleToTrianglesMap triangles_intersection(const std::vector<Triangle_as_Node> &triangles , const std::vector<Triangle_as_Point> &triangles_pos);