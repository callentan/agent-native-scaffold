using Flagsmith;
using Microsoft.Extensions.Logging;
using OpenFeature;
using OpenFeature.Contrib.Providers.Flagsmith;

public sealed class EnvironmentDocumentOnlyHandler(
    Uri apiUri, HttpMessageHandler transport, ILogger logger) : DelegatingHandler(transport)
{
    private readonly Uri _documentUri = new(apiUri, "environment-document/");

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        if (request.Method != HttpMethod.Get || request.RequestUri is null
            || !request.RequestUri.Equals(_documentUri))
        {
            logger.LogWarning("Blocked a non-document request in local-only evaluation mode.");
            throw new HttpRequestException("Remote flag evaluation is disabled.");
        }

        return base.SendAsync(request, cancellationToken);
    }
}

public static class LocalEvaluation
{
    public static HttpClient CreateGuardedHttpClient(Uri apiUri, ILogger logger) =>
        new(new EnvironmentDocumentOnlyHandler(
            apiUri,
            new SocketsHttpHandler { AllowAutoRedirect = false },
            logger))
        { Timeout = TimeSpan.FromSeconds(2) };

    public static FlagsmithClient CreateClient(
        Uri apiUri,
        string environmentKey,
        HttpClient guardedHttp,
        ILogger sdkLogger,
        bool isDevelopment,
        int refreshSeconds = 10)
    {
        ValidateApiUri(apiUri, isDevelopment);
        ValidateEnvironmentKey(environmentKey);
        ArgumentNullException.ThrowIfNull(guardedHttp);
        ArgumentNullException.ThrowIfNull(sdkLogger);
        if (refreshSeconds < 5)
            throw new ArgumentOutOfRangeException(nameof(refreshSeconds),
                "The refresh interval must be at least five seconds.");

        return new FlagsmithClient(new FlagsmithConfiguration
        {
            ApiUri = apiUri,
            EnvironmentKey = environmentKey,
            EnableLocalEvaluation = true,
            EnvironmentRefreshInterval = TimeSpan.FromSeconds(refreshSeconds),
            RequestTimeout = 2,
            Retries = 0,
            EnableAnalytics = false,
            HttpClient = guardedHttp,
            Logger = sdkLogger
        });
    }

    public static async Task VerifyAndRegisterAsync(
        FlagsmithClient client, string requiredFlag)
    {
        ArgumentNullException.ThrowIfNull(client);
        if (string.IsNullOrWhiteSpace(requiredFlag))
            throw new ArgumentException("A required startup flag is needed.", nameof(requiredFlag));

        var flags = await client.GetEnvironmentFlags();
        if (!flags.AllFlags().Any(flag =>
                string.Equals(flag.GetFeatureName(), requiredFlag, StringComparison.Ordinal)))
            throw new InvalidOperationException("The required backend demo flag is missing.");

        // Evaluate the approved flag from the loaded document; either Boolean state is valid.
        _ = await flags.IsFeatureEnabled(requiredFlag);

        await Api.Instance.SetProviderAsync(new FlagsmithProvider(
            new FlagsmithProviderConfiguration { UsingBooleanConfigValue = false }, client));
    }

    public static void ValidateConfiguration(
        Uri apiUri, string environmentKey, bool isDevelopment, int refreshSeconds)
    {
        ValidateApiUri(apiUri, isDevelopment);
        ValidateEnvironmentKey(environmentKey);
        if (refreshSeconds < 5)
            throw new ArgumentOutOfRangeException(nameof(refreshSeconds),
                "The refresh interval must be at least five seconds.");
    }

    private static void ValidateApiUri(Uri apiUri, bool isDevelopment)
    {
        ArgumentNullException.ThrowIfNull(apiUri);
        var https = string.Equals(apiUri.Scheme, Uri.UriSchemeHttps, StringComparison.OrdinalIgnoreCase);
        var developmentHttp = isDevelopment
            && string.Equals(apiUri.Scheme, Uri.UriSchemeHttp, StringComparison.OrdinalIgnoreCase)
            && IsLiteralLoopback(apiUri.Host);

        if ((!https && !developmentHttp)
            || !apiUri.AbsolutePath.EndsWith("/api/v1/", StringComparison.Ordinal)
            || !string.IsNullOrEmpty(apiUri.UserInfo)
            || !string.IsNullOrEmpty(apiUri.Query)
            || !string.IsNullOrEmpty(apiUri.Fragment))
            throw new ArgumentException(
                "An explicit HTTPS /api/v1/ URL is required; HTTP is limited to Development loopback.",
                nameof(apiUri));
    }

    private static bool IsLiteralLoopback(string host) =>
        string.Equals(host, "localhost", StringComparison.OrdinalIgnoreCase)
        || string.Equals(host, "127.0.0.1", StringComparison.Ordinal)
        || string.Equals(host, "::1", StringComparison.Ordinal);

    private static void ValidateEnvironmentKey(string environmentKey)
    {
        if (string.IsNullOrWhiteSpace(environmentKey)
            || !environmentKey.StartsWith("ser.", StringComparison.Ordinal)
            || environmentKey.Any(char.IsWhiteSpace))
            throw new ArgumentException("A non-empty server-side Flagsmith key is required.",
                nameof(environmentKey));
    }
}

public interface IFeatureFlagsHttpClientFactory
{
    HttpClient Create(Uri apiUri, ILogger logger);
}

public sealed class FeatureFlagsHttpClientFactory : IFeatureFlagsHttpClientFactory
{
    public HttpClient Create(Uri apiUri, ILogger logger) =>
        LocalEvaluation.CreateGuardedHttpClient(apiUri, logger);
}
