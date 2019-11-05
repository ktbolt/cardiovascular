
import shape

#print(dir(shape))

square = shape.Square(2.0)
s_area = square.Area()
print("Square area: {0:f}".format(s_area))

circle = shape.Circle(2.0)
c_area = circle.Area()
c_list = circle.GetList()
print("Circle area: {0:s}".format(str(c_list)))


