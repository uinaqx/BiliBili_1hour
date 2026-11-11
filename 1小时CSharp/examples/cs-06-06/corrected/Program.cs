var wallet = new Wallet();
wallet.Add(12);
Console.WriteLine(wallet.Balance);
class Wallet
{
    public int Balance { get; private set; }
    public void Add(int value) { Balance += value; }
}
