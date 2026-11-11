var alarm = new Alarm();
alarm.Triggered += () => Console.WriteLine("预算提醒");
alarm.Raise();
class Alarm
{
    public event Action? Triggered;
    public void Raise() => Triggered?.Invoke();
}
