using Fixtures;
using Xunit;

public sealed class LocalEvaluationTests
{
    [Theory]
    [InlineData("startup-off")]
    [InlineData("startup-on")]
    public async Task StartupAcceptsEitherKnownBooleanState(string mode)
    {
        var result = await RunChildAsync(mode, expectSuccess: true);
        Assert.Contains("STARTUP_OK", result.StandardOutput, StringComparison.Ordinal);
    }

    [Theory]
    [InlineData("missing-document")]
    [InlineData("malformed-document")]
    [InlineData("redirect")]
    public async Task UnsafeOrInvalidDocumentsFailWithoutFallback(string mode)
    {
        var result = await RunChildAsync(mode, expectSuccess: false);
        Assert.Contains("REMOTE_REQUESTS=0", result.StandardError, StringComparison.Ordinal);
        Assert.Contains("CHILD_ERROR=", result.StandardError, StringComparison.Ordinal);
    }

    [Fact]
    public async Task DistinctInvocationContextsRemainStableAndMakeNoHotPathRequests()
    {
        var result = await RunChildAsync("identity", expectSuccess: true);
        Assert.Contains("IDENTITY_RESULTS=beta:new,control:legacy;REPEATS=10", result.StandardOutput,
            StringComparison.Ordinal);
    }

    [Fact]
    public async Task InformationDocumentDataIsFilteredAndWarningsRemainObservable()
    {
        var result = await RunChildAsync("logging", expectSuccess: true);
        Assert.Contains("INFO_FILTERED=True", result.StandardOutput, StringComparison.Ordinal);
        Assert.Contains("WARNING_OBSERVED=True", result.StandardOutput, StringComparison.Ordinal);
    }

    [Fact]
    public async Task PostStartEvaluationErrorReturnsLegacyAndLogsOnce()
    {
        var result = await RunChildAsync("post-start-error", expectSuccess: true);
        Assert.Contains("REPLY_MODE=legacy;REPLY_MESSAGE=Backend: legacy", result.StandardOutput,
            StringComparison.Ordinal);
        Assert.Contains("ERROR_LOGS=1", result.StandardOutput, StringComparison.Ordinal);
    }

    [Fact]
    public void UnsafeConfigurationIsRejectedBeforeTransportCreation()
    {
        Assert.Throws<ArgumentException>(() => LocalEvaluation.ValidateConfiguration(
            new Uri("http://remote.example/api/v1/"), "ser.key", isDevelopment: true, 10));
        Assert.Throws<ArgumentException>(() => LocalEvaluation.ValidateConfiguration(
            new Uri("https://flags.example/api/v1/?unsafe=true"), "ser.key", isDevelopment: false, 10));
        Assert.Throws<ArgumentException>(() => LocalEvaluation.ValidateConfiguration(
            new Uri("https://flags.example/api/v1/"), "cli.key", isDevelopment: false, 10));
    }

    private static async Task<ChildResult> RunChildAsync(string mode, bool expectSuccess)
    {
        var assemblyPath = Path.GetFullPath(Path.Combine(
            AppContext.BaseDirectory, "..", "..", "..", "Fixtures", "LocalEvaluationChild",
            "bin", "Debug", "net10.0", "Poc.Api.LocalEvaluation.Child.dll"));
        var workingDirectory = Path.GetDirectoryName(assemblyPath)
            ?? throw new InvalidOperationException("The child working directory is unavailable.");
        var process = await BackendProcess.StartCommandAsync(
            assemblyPath, workingDirectory, [mode]);
        try
        {
            await process.WaitForExitAsync(TimeSpan.FromSeconds(20));
            var result = new ChildResult(process.ExitCode, process.StandardOutput, process.StandardError);
            Assert.Equal(expectSuccess, result.ExitCode == 0);
            return result;
        }
        finally
        {
            await process.DisposeAsync();
        }
    }

    private sealed record ChildResult(int ExitCode, string StandardOutput, string StandardError);
}
