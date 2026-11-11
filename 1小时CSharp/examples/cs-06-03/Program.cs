var wallet = new Wallet(30);
wallet.Spend(12);
Console.WriteLine(wallet.Balance);
class Wallet
{
    public int Balance { get; private set; }
    public Wallet(int balance) { Balance = balance; }
    public void Spend(int amount) { Balance -= amount; }
}
