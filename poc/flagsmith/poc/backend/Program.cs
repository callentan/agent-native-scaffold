using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using OpenFeature;
using OpenFeature.Model;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.AddFilter("FlagsmithSdk", LogLevel.Warning);
builder.Services.AddSingleton<IFeatureFlagsHttpClientFactory, FeatureFlagsHttpClientFactory>();
builder.Services.AddSingleton<FeatureClient>(_ => Api.Instance.GetClient());

var fixturePath = Path.Combine(AppContext.BaseDirectory, "demo-users.json");
var demoUsers = DemoUsers.Load(fixturePath);
builder.Services.AddSingleton(demoUsers);

var app = builder.Build();

app.MapGet("/api/demo", async (
    string? userId,
    DemoUsers users,
    FeatureClient featureClient,
    ILogger<Program> logger,
    HttpResponse response) =>
{
    var user = users.Find(userId);
    if (user is null)
        return Results.Problem(statusCode: StatusCodes.Status400BadRequest,
            title: "Unknown demo user.");

    var reply = await DemoDecision.EvaluateAsync(user, featureClient, logger);
    response.Headers.CacheControl = "no-store";
    return Results.Ok(reply);
});

var featureFlags = app.Configuration.GetSection("FeatureFlags");
var apiUrlText = featureFlags["ApiUrl"]
    ?? throw new InvalidOperationException("FeatureFlags:ApiUrl is required.");
if (!Uri.TryCreate(apiUrlText, UriKind.Absolute, out var apiUri))
    throw new InvalidOperationException("FeatureFlags:ApiUrl must be an absolute URI.");
var environmentKey = ServerKeyConfiguration.Require(
    ServerKeyConfiguration.Load(builder.Environment));
var refreshSeconds = featureFlags.GetValue<int?>("RefreshSeconds")
    ?? throw new InvalidOperationException("FeatureFlags:RefreshSeconds is required.");
var isDevelopment = app.Environment.IsDevelopment();
LocalEvaluation.ValidateConfiguration(apiUri, environmentKey, isDevelopment, refreshSeconds);
var loggerFactory = app.Services.GetRequiredService<ILoggerFactory>();
var httpFactory = app.Services.GetRequiredService<IFeatureFlagsHttpClientFactory>();
var guardedHttp = httpFactory.Create(apiUri, loggerFactory.CreateLogger("FeatureFlags"));
var flagsmith = LocalEvaluation.CreateClient(
    apiUri,
    environmentKey,
    guardedHttp,
    loggerFactory.CreateLogger("FlagsmithSdk"),
    app.Environment.IsDevelopment(),
    refreshSeconds);

try
{
    await LocalEvaluation.VerifyAndRegisterAsync(flagsmith, "backend_demo_v2");
    await app.RunAsync();
}
finally
{
    await Api.Instance.ShutdownAsync();
}

public partial class Program;
