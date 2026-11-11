IMessage message = new Welcome();
message.Show();
interface IMessage { void Show(); }
class Welcome : IMessage
{
    public void Show() => Console.WriteLine("欢迎学习");
}
