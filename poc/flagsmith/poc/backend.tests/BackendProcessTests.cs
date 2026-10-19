using Fixtures;
using Xunit;

public sealed class BackendProcessTests
{
    [Theory]
    [InlineData("relative", 1)]
    [InlineData("absolute", 0)]
    public async Task InvalidReadinessInputDoesNotStartAChild(string uriKind, int timeoutSeconds)
    {
        var assemblyPath = Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory, "..", "..", "..", "Fixtures", "LocalEvaluationChild",
            "bin", "Debug", "net10.0", "Poc.Api.LocalEvaluation.Child.dll"));
        var workingDirectory = Path.GetDirectoryName(assemblyPath)!;
        var readiness = uriKind == "relative"
            ? new Uri("/ready", UriKind.Relative)
            : new Uri("https://127.0.0.1/ready");
        var activeBefore = BackendProcess.ActiveProcessCount;

        await Assert.ThrowsAnyAsync<ArgumentException>(() => BackendProcess.StartAsync(
            assemblyPath, workingDirectory, readiness, TimeSpan.FromSeconds(timeoutSeconds)));

        Assert.Equal(activeBefore, BackendProcess.ActiveProcessCount);
    }
}