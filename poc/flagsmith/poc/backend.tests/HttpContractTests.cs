using Fixtures;
using Xunit;

public sealed class HttpContractTests
{
    [Fact]
    public async Task HttpContractsRunInAnOwnedNativeSdkChild()
    {
        var assemblyPath = Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory, "..", "..", "..", "Fixtures", "HttpContractChild",
            "bin", "Debug", "net10.0", "Poc.Api.HttpContract.Child.dll"));
        var workingDirectory = Path.GetDirectoryName(assemblyPath)
            ?? throw new InvalidOperationException("The HTTP child working directory is unavailable.");
        var process = await BackendProcess.StartCommandAsync(
            assemblyPath, workingDirectory, []);
        try
        {
            await process.WaitForExitAsync(TimeSpan.FromSeconds(20));
            Assert.True(process.ExitCode == 0, $"stdout: {process.StandardOutput} stderr: {process.StandardError}");
            Assert.Contains("HTTP_CONTRACTS_OK", process.StandardOutput, StringComparison.Ordinal);
        }
        finally
        {
            await process.DisposeAsync();
        }
    }
}