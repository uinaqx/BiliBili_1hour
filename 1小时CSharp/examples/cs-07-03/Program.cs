Shape shape = new Square(3);
Console.WriteLine(shape.Area());
abstract class Shape
{
    public abstract int Area();
}
class Square : Shape
{
    private int side;
    public Square(int value) { side = value; }
    public override int Area() => side * side;
}
