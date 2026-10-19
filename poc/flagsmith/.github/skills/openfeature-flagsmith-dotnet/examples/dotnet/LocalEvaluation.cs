using Flagsmith;
using Microsoft.Extensions.Logging;
using OpenFeature;
using OpenFeature.Contrib.Providers.Flagsmith;

namespace FeatureFlagReference;

public sealed class EnvironmentDocumentOnlyHandler(
    Uri apiUri, HttpMessageHandler transport, ILogger logger) : DelegatingHandler(transport)
{
    private readonly Uri documentUri = new(apiUri, "environment-document/");

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
    {
        if (request.Method != HttpMethod.Get || request.RequestUri != documentUri)
        {
            logger.LogWarning("Blocked a non-document request in local-only evaluation mode.");
            throw new HttpRequestException("Remote flag evaluation is disabled.");
        }
        return base.SendAsync(request, cancellationToken);
    }
}

public static class LocalEvaluation
{
    public static FlagsmithClient CreateClient(
        Uri apiUri, string environmentKey, HttpClient guardedHttp, ILogger sdkLogger,
        int refreshSeconds = 30)
    {
        if (!apiUri.IsAbsoluteUri || apiUri.Scheme != Uri.UriSchemeHttps
            || !apiUri.AbsolutePath.EndsWith("/api/v1/", StringComparison.Ordinal)
            || !string.IsNullOrEmpty(apiUri.UserInfo) || !string.IsNullOrEmpty(apiUri.Query)
            || !string.IsNullOrEmpty(apiUri.Fragment))
            throw new ArgumentException("An explicit HTTPS /api/v1/ URL is required.", nameof(apiUri));
        if (!environmentKey.StartsWith("ser.", StringComparison.Ordinal) || refreshSeconds < 5)
            throw new ArgumentException("A server-side key and refresh interval of at least five seconds are required.");

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
        FlagsmithClient client, string smokeFlag, bool expectedValue)
    {
        // This call can fall back remotely in the SDK; the HTTP guard makes that impossible.
        var flags = await client.GetEnvironmentFlags();
        if (await flags.IsFeatureEnabled(smokeFlag) != expectedValue)
            throw new InvalidOperationException("The approved local smoke flag has an unexpected value.");
        await Api.Instance.SetProviderAsync(new FlagsmithProvider(
            new FlagsmithProviderConfiguration { UsingBooleanConfigValue = false }, client));
    }
}
