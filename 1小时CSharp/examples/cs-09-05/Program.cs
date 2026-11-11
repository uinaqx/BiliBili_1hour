string path = "async-note.txt";
await File.WriteAllTextAsync(path, "记录完成");
string text = await File.ReadAllTextAsync(path);
Console.WriteLine(text);
static async Task<int> LoadAmountAsync()
{
    await Task.Delay(10);
    return 12;
}
Console.WriteLine(await LoadAmountAsync());
