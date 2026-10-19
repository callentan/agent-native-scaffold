using System.Net;
using FeatureFlagReference;
using Microsoft.Extensions.Logging;
using OpenFeature;
using OpenFeature.Model;

var failures = 0;
await Check("Cold startup rejects missing documents even when /flags would succeed", async () =>
{
    var transport = new SyntheticTransport(documentAvailable: false);
    var output = new CapturedLogs();
    using var logging = CreateLogging(output);
    using var http = GuardedHttp(transport, logging);
    var client = LocalEvaluation.CreateClient(ApiUri(), "ser.synthetic-test-key", http,
        logging.CreateLogger("FlagsmithSdk"), refreshSeconds: 3600);
    var rejected = false;
    try
    {
        await LocalEvaluation.VerifyAndRegisterAsync(client, "checkout_v2", true);
    }
    catch (Flagsmith.FlagsmithAPIError)
    {
        rejected = true;
    }
    Require(rejected, "Missing documents must fail startup.");
    Require(transport.RemoteRequests == 0, "Remote evaluation reached the transport.");
    Require(output.Messages.Any(message => message.Contains("Blocked", StringComparison.Ordinal)),
        "Blocked fallback must be observable.");
});

await Check("A valid document supports OpenFeature identity evaluation without network calls", async () =>
{
    var transport = new SyntheticTransport(documentAvailable: true);
    var output = new CapturedLogs();
    using var logging = CreateLogging(output);
    using var http = GuardedHttp(transport, logging);
    var client = LocalEvaluation.CreateClient(ApiUri(), "ser.synthetic-test-key", http,
        logging.CreateLogger("FlagsmithSdk"), refreshSeconds: 3600);
    await LocalEvaluation.VerifyAndRegisterAsync(client, "checkout_v2", true);
    try
    {
        var callsAfterStartup = transport.TotalRequests;
        var featureClient = Api.Instance.GetClient();
        var contexts = new[] { "tenant-a:user-1", "tenant-b:user-1" }
            .Select(key => EvaluationContext.Builder().SetTargetingKey(key).Build());
        foreach (var context in contexts)
        {
            var details = await featureClient.GetBooleanDetailsAsync("checkout_v2", false, context);
            Require(details.ErrorType == OpenFeature.Constant.ErrorType.None && details.Value,
                "Local evaluation must return the real enabled state.");
        }
        var missing = await featureClient.GetBooleanDetailsAsync("missing_flag", false);
        Require(!missing.Value && missing.ErrorType != OpenFeature.Constant.ErrorType.None,
            "Unknown flags must return the default with observable error details.");
        Require(transport.TotalRequests == callsAfterStartup && transport.RemoteRequests == 0,
            "The evaluation hot path made an HTTP request.");
        Require(!output.Messages.Any(message => message.Contains("feature_states", StringComparison.Ordinal)),
            "The SDK logged a complete environment document.");
        logging.CreateLogger("FlagsmithSdk").LogWarning("Synthetic refresh failure.");
        Require(output.Messages.Contains("Synthetic refresh failure."),
            "SDK warning diagnostics must not be suppressed.");
    }
    finally
    {
        await Api.Instance.ShutdownAsync();
    }
});

await Check("The guard rejects wrong methods, paths, and origins before transport", async () =>
{
    var transport = new SyntheticTransport(documentAvailable: true);
    using var logging = CreateLogging(new CapturedLogs());
    using var http = GuardedHttp(transport, logging);
    foreach (var (method, url) in new[]
    {
        (HttpMethod.Get, "https://flags.internal.example/api/v1/flags/"),
        (HttpMethod.Post, "https://flags.internal.example/api/v1/environment-document/"),
        (HttpMethod.Get, "https://other.example/api/v1/environment-document/")
    })
    {
        var rejected = false;
        try { using var response = await http.SendAsync(new HttpRequestMessage(method, url)); }
        catch (HttpRequestException) { rejected = true; }
        Require(rejected, "A non-document request was accepted.");
    }
    Require(transport.TotalRequests == 0, "The guard leaked an HTTP request.");
});

Console.WriteLine(failures == 0 ? "All .NET reference checks passed." : $"{failures} .NET checks failed.");
return failures == 0 ? 0 : 1;

async Task Check(string name, Func<Task> action)
{
    try { await action(); Console.WriteLine($"PASS: {name}"); }
    catch (Exception error)
    {
        failures++;
        Console.Error.WriteLine($"FAIL: {name}: {error}");
    }
}
static void Require(bool condition, string message)
{
    if (!condition) throw new InvalidOperationException(message);
}
static Uri ApiUri() => new("https://flags.internal.example/api/v1/");
static ILoggerFactory CreateLogging(CapturedLogs output) => LoggerFactory.Create(builder =>
    builder.SetMinimumLevel(LogLevel.Information)
        .AddFilter("FlagsmithSdk", LogLevel.Warning)
        .AddProvider(output));
static HttpClient GuardedHttp(SyntheticTransport transport, ILoggerFactory logging) =>
    new(new EnvironmentDocumentOnlyHandler(ApiUri(), transport, logging.CreateLogger("FeatureFlags")))
    { Timeout = TimeSpan.FromSeconds(2) };

sealed class SyntheticTransport(bool documentAvailable) : HttpMessageHandler
{
    public int RemoteRequests { get; private set; }
    public int TotalRequests { get; private set; }
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        TotalRequests++;
        if (request.RequestUri!.AbsolutePath.EndsWith("/environment-document/", StringComparison.Ordinal))
            return Task.FromResult(new HttpResponseMessage(documentAvailable
                ? HttpStatusCode.OK : HttpStatusCode.ServiceUnavailable)
            { Content = new StringContent(Document) });
        RemoteRequests++;
        return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
        { Content = new StringContent("[]") });
    }
    private const string Document = """
        {
          "id": 1, "api_key": "ser.synthetic-test-key", "name": "Synthetic test",
          "project": {
            "id": 1, "name": "Reference", "hide_disabled_flags": false, "segments": [],
            "organisation": {
              "id": 1, "name": "Reference", "feature_analytics": false,
              "persist_trait_data": false, "stop_serving_flags": false
            }
          },
          "segment_overrides": [], "identity_overrides": [],
          "feature_states": [{
            "id": 1, "enabled": true, "feature_state_value": null,
            "multivariate_feature_state_values": [],
            "feature": { "id": 1, "name": "checkout_v2", "type": "STANDARD" }
          }]
        }
        """;
}

sealed class CapturedLogs : ILoggerProvider
{
    public List<string> Messages { get; } = [];
    public ILogger CreateLogger(string categoryName) => new CaptureLogger(Messages);
    public void Dispose() {}
    private sealed class CaptureLogger(List<string> messages) : ILogger
    {
        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
        public bool IsEnabled(LogLevel logLevel) => true;
        public void Log<TState>(LogLevel level, EventId id, TState state, Exception? exception,
            Func<TState, Exception?, string> formatter) => messages.Add(formatter(state, exception));
    }
}
