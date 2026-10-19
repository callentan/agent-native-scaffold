using System.Collections.Concurrent;
using System.Net;
using Microsoft.Extensions.Logging;
using OpenFeature;
using OpenFeature.Model;

const string ApiUrl = "https://flags.synthetic.example/api/v1/";
const string Key = "ser.synthetic-test-key";
var mode = args.FirstOrDefault() ?? throw new ArgumentException("A child test mode is required.");
var capturedLogs = new CapturedLogs();
var transport = new SyntheticTransport(mode);
using var logging = LoggerFactory.Create(builder => builder
    .SetMinimumLevel(LogLevel.Information)
    .AddFilter("FlagsmithSdk", LogLevel.Warning)
    .AddProvider(capturedLogs));
using var http = new HttpClient(new EnvironmentDocumentOnlyHandler(
    new Uri(ApiUrl), transport, logging.CreateLogger("FeatureFlags")))
{ Timeout = TimeSpan.FromSeconds(2) };
Flagsmith.FlagsmithClient? client = null;
try
{
    client = LocalEvaluation.CreateClient(
        new Uri(ApiUrl), Key, http, logging.CreateLogger("FlagsmithSdk"),
        isDevelopment: false, refreshSeconds: 3600);
    await LocalEvaluation.VerifyAndRegisterAsync(client, "backend_demo_v2");
    var featureClient = Api.Instance.GetClient();
    switch (mode)
    {
        case "startup-off":
        case "startup-on":
            Console.WriteLine("STARTUP_OK");
            break;
        case "identity":
            await RunIdentityChecks(featureClient, transport);
            break;
        case "logging":
            logging.CreateLogger("FlagsmithSdk").LogWarning("synthetic-warning-marker");
            Console.WriteLine($"INFO_FILTERED={!capturedLogs.Messages.Any(message =>
                message.Contains("feature_states", StringComparison.Ordinal)
                || message.Contains(Key, StringComparison.Ordinal))}");
            Console.WriteLine($"WARNING_OBSERVED={capturedLogs.Messages.Contains(
                "synthetic-warning-marker", StringComparer.Ordinal)}");
            break;
        case "post-start-error":
            await Api.Instance.SetProviderAsync(new FailingProvider());
            var reply = await DemoDecision.EvaluateAsync(
                new DemoUser("demo-user-001", "User 001", true), featureClient,
                logging.CreateLogger("BackendDemo"));
            Console.WriteLine($"REPLY_MODE={reply.Mode};REPLY_MESSAGE={reply.Message}");
            Console.WriteLine($"ERROR_LOGS={capturedLogs.Messages.Count(message =>
                message.Contains("Backend demo flag evaluation failed", StringComparison.Ordinal))}");
            break;
        default:
            throw new ArgumentException($"Unknown child test mode: {mode}");
    }

    if (mode is "missing-document" or "malformed-document" or "redirect")
        throw new InvalidOperationException("The invalid startup mode unexpectedly succeeded.");
    return 0;
}
catch (Exception error)
{
    Console.Error.WriteLine($"CHILD_ERROR={error.GetType().Name}:{error.Message}");
    Console.Error.WriteLine(error.ToString());
    Console.Error.WriteLine($"REMOTE_REQUESTS={transport.RemoteRequests}");
    return 1;
}
finally
{
    await Api.Instance.ShutdownAsync();
}

static async Task RunIdentityChecks(FeatureClient featureClient, SyntheticTransport transport)
{
    var users = new[]
    {
        new DemoUser("beta-user", "Beta", true),
        new DemoUser("control-user", "Control", true)
    };
    var requestsAfterStartup = transport.TotalRequests;
    var evaluations = await Task.WhenAll(
        Enumerable.Range(0, 10).SelectMany(_ => users.Select(async user =>
        {
            var reply = await DemoDecision.EvaluateAsync(user, featureClient,
                NullLogger.Instance);
            return (user.Id, user.Beta, reply.Mode);
        })));

    foreach (var evaluation in evaluations)
    {
        var expected = evaluation.Id == "beta-user" ? "new" : "legacy";
        if (!string.Equals(evaluation.Mode, expected, StringComparison.Ordinal))
            throw new InvalidOperationException(
                $"Unexpected decision for {evaluation.Id}: {evaluation.Mode}");
    }
    if (transport.TotalRequests != requestsAfterStartup)
        throw new InvalidOperationException("Invocation evaluation made an HTTP request.");
    Console.WriteLine("IDENTITY_RESULTS=beta:new,control:legacy;REPEATS=10;CONCURRENT=True;HOT_PATH_REQUESTS=0");
}
sealed class SyntheticTransport(string mode) : HttpMessageHandler
{
    private int _remoteRequests;
    private int _totalRequests;
    public int RemoteRequests => Volatile.Read(ref _remoteRequests);
    public int TotalRequests => Volatile.Read(ref _totalRequests);

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        Interlocked.Increment(ref _totalRequests);
        if (request.RequestUri?.AbsolutePath.EndsWith(
                "/environment-document/", StringComparison.Ordinal) != true)
        {
            Interlocked.Increment(ref _remoteRequests);
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            { Content = new StringContent("[]") });
        }

        if (mode == "missing-document")
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.ServiceUnavailable));
        if (mode == "redirect")
        {
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.Redirect)
            { Headers = { Location = new Uri("https://other.example/api/v1/environment-document/") } });
        }
        if (mode == "malformed-document")
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            { Content = new StringContent("not-json") });

        return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
        { Content = new StringContent(Document) });
    }

    private string Document => """
    {
      "id": 1, "api_key": "ser.synthetic-test-key", "name": "Synthetic test",
      "project": {
        "id": 1, "name": "Reference", "hide_disabled_flags": false, "segments": [],
                "organisation": { "id": 1, "name": "Reference", "feature_analytics": false,
          "persist_trait_data": false, "stop_serving_flags": false }
      },
      "segment_overrides": [], "identity_overrides": [{
        "identifier": "beta-user", "environment_api_key": "ser.synthetic-test-key",
        "identity_uuid": "0f21cde8-63c5-4e50-baca-87897fa6cd01",
        "created_date": "2019-08-27T14:53:45.698555Z",
        "updated_at": "2023-07-14T16:12:00.000000",
        "identity_features": [{
          "id": 2, "django_id": 2, "featurestate_uuid": "2bddb9a5-7e59-42c6-9be9-625fa369749f",
          "enabled": true, "feature_state_value": null,
          "environment": 1, "identity": null, "feature_segment": null,
          "multivariate_feature_state_values": [],
          "feature": { "id": 1, "name": "backend_demo_v2", "type": "STANDARD" }
        }], "identity_traits": []
      }],
      "feature_states": [{
        "id": 1, "django_id": 1, "featurestate_uuid": "1bddb9a5-7e59-42c6-9be9-625fa369749f",
        "enabled": __DEFAULT_ENABLED__, "feature_state_value": null,
        "multivariate_feature_state_values": [],
        "feature": { "id": 1, "name": "backend_demo_v2", "key": "backend_demo_v2", "type": "STANDARD" }
      }]
    }
    """.Replace("__DEFAULT_ENABLED__", mode == "startup-on" ? "true" : "false",
        StringComparison.Ordinal);
}

sealed class CapturedLogs : ILoggerProvider
{
    public ConcurrentBag<string> Messages { get; } = [];
    public ILogger CreateLogger(string categoryName) => new CaptureLogger(Messages);
    public void Dispose() { }

    private sealed class CaptureLogger(ConcurrentBag<string> messages) : ILogger
    {
        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
        public bool IsEnabled(LogLevel logLevel) => true;
        public void Log<TState>(LogLevel level, EventId id, TState state,
            Exception? exception, Func<TState, Exception?, string> formatter) =>
            messages.Add(formatter(state, exception));
    }
}

sealed class NullLogger : ILogger
{
    public static NullLogger Instance { get; } = new();
    public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;
    public bool IsEnabled(LogLevel logLevel) => false;
    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state,
        Exception? exception, Func<TState, Exception?, string> formatter) { }
}

sealed class FailingProvider : FeatureProvider
{
    public override Metadata GetMetadata() => new("test-failure-provider");
    public override Task<ResolutionDetails<bool>> ResolveBooleanValueAsync(
        string flagKey, bool defaultValue, EvaluationContext? context, CancellationToken cancellationToken) =>
        Task.FromResult(new ResolutionDetails<bool>(flagKey, defaultValue,
            OpenFeature.Constant.ErrorType.General, "Synthetic post-start failure",
            "test", "test", new ImmutableMetadata()));
    public override Task<ResolutionDetails<string>> ResolveStringValueAsync(
        string flagKey, string defaultValue, EvaluationContext? context, CancellationToken cancellationToken) =>
        throw new NotSupportedException();
    public override Task<ResolutionDetails<int>> ResolveIntegerValueAsync(
        string flagKey, int defaultValue, EvaluationContext? context, CancellationToken cancellationToken) =>
        throw new NotSupportedException();
    public override Task<ResolutionDetails<double>> ResolveDoubleValueAsync(
        string flagKey, double defaultValue, EvaluationContext? context, CancellationToken cancellationToken) =>
        throw new NotSupportedException();
    public override Task<ResolutionDetails<Value>> ResolveStructureValueAsync(
        string flagKey, Value defaultValue, EvaluationContext? context, CancellationToken cancellationToken) =>
        throw new NotSupportedException();
}
