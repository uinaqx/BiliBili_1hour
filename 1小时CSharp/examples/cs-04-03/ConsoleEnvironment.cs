internal static class ConsoleEnvironment
{
    [System.Runtime.CompilerServices.ModuleInitializer]
    internal static void Initialize()
    {
        System.Console.InputEncoding = new System.Text.UTF8Encoding(false);
        System.Console.OutputEncoding = new System.Text.UTF8Encoding(false);
        System.Globalization.CultureInfo.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
    }
}
