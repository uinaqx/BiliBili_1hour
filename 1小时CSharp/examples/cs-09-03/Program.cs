string path = "note.txt";
File.WriteAllText(path, "午餐：12");
string text = File.ReadAllText(path);
Console.WriteLine(text);
