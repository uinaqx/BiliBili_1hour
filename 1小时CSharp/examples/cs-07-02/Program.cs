Animal pet = new Cat();
pet.Speak();
class Animal
{
    public virtual void Speak() => Console.WriteLine("动物发声");
}
class Cat : Animal
{
    public override void Speak() => Console.WriteLine("喵");
}
