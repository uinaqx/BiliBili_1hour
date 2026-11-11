var student = new Student { Name = "小林", Score = 80 };
Console.WriteLine($"{student.Name} {student.Score}");
class Person
{
    public string Name { get; set; } = "";
}
class Student : Person
{
    public int Score { get; set; }
}
