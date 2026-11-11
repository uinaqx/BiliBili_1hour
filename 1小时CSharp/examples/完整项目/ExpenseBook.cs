using System.Text.Json;
namespace ExpenseCourse;

public class ExpenseBook
{
    private readonly string path;
    private List<Expense> items = new();
    public string LoadMessage { get; private set; } = "";
    public bool CanSave { get; private set; } = true;
    public IReadOnlyList<Expense> Items => items.AsReadOnly();
    public decimal Total => items.Sum(item => item.Amount);

    public ExpenseBook(string path)
    {
        this.path = Path.GetFullPath(path);
        if (!File.Exists(this.path)) return;
        try
        {
            var loaded = JsonSerializer.Deserialize<List<Expense>>(File.ReadAllText(this.path));
            if (loaded is null || loaded.Any(item => item is null || item.Id <= 0
                || string.IsNullOrWhiteSpace(item.Name) || item.Amount < 0)
                || loaded.Select(item => item.Id).Distinct().Count() != loaded.Count)
                throw new InvalidDataException("记录字段或编号有误");
            items = loaded;
        }
        catch (Exception error) when (error is JsonException or InvalidDataException or IOException or UnauthorizedAccessException)
        {
            LoadMessage = "读取记录失败：" + error.Message;
            try
            {
                string backup = this.path + ".invalid-" + Guid.NewGuid().ToString("N") + ".json";
                File.Move(this.path, backup);
                LoadMessage += "。原文件已保留为 " + Path.GetFileName(backup) + "，当前从空列表开始。";
            }
            catch (Exception backupError) when (backupError is IOException or UnauthorizedAccessException)
            {
                CanSave = false;
                LoadMessage += "。原文件已保留，当前仅在内存中操作：" + backupError.Message;
            }
        }
    }

    public Expense Add(string name, decimal amount)
    {
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("请输入名称", nameof(name));
        if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
        int id = checked((items.Count == 0 ? 0 : items.Max(item => item.Id)) + 1);
        var item = new Expense { Id = id, Name = name.Trim(), Amount = amount };
        items.Add(item);
        return item;
    }
    public bool Remove(int id) => items.RemoveAll(item => item.Id == id) > 0;
    public async Task SaveAsync()
    {
        if (!CanSave) throw new IOException("原文件读取或备份失败，请更换保存位置后重试");
        string? directory = Path.GetDirectoryName(path);
        if (directory is not null) Directory.CreateDirectory(directory);
        string json = JsonSerializer.Serialize(items, new JsonSerializerOptions { WriteIndented = true });
        await File.WriteAllTextAsync(path, json);
    }
}
