
import shape

#print(dir(shape))

square = shape.Square(2.0)
sarea = square.area()
print("Square area: {0:f}".format(sarea))

circle = shape.Circle(2.0)
carea = circle.area()
print("Circle area: {0:f}".format(carea))


