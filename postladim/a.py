from typing import Tuple, Union


Point2 = Tuple[int, int]
Point3 = Tuple[int, int, int]

#Point = Union[Point2, Point3]
Point = Tuple[int, ...]

#point: Point = (2,4, 4)
point = (2,3,4)

x, y, z = point

#if len(point) == 2:
# if isinstance(point, Point2):
#     #point_2: Point2 = point
#     x, y = point
# if len(point) == 3:
#     x, y, z = point

print(x)
