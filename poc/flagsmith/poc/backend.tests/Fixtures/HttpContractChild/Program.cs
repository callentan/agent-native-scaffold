using System.Net;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;

namespace HttpContractChild;

public static class EntryPoint
{
    public static async Task<int> Main()
    {
        const string variable = "FeatureFlags__EnvironmentKey";
        var previous = Environment.GetEnvironmentVariable(variable);
        Environment.SetEnvironmentVariable(variable, "ser.synthetic-test-key");
        try
        {
            using var factory = new SyntheticWebFactory();
            using var client = factory.CreateClient();
            foreach (var path in new[]
            {
                "/api/demo", "/api/demo?userId=", "/api/demo?userId=unknown",
                "/api/demo?userId=demo-user-001%20"
            })
            {
                using var response = await client.GetAsync(path);
                var body = await response.Content.ReadAsStringAsync();
                if (response.StatusCode != HttpStatusCode.BadRequest
                    || !body.Contains("Unknown demo user.", StringComparison.Ordinal))
                    throw new InvalidOperationException("Invalid user contract failed.");
            }

            using var success = await client.GetAsync("/api/demo?userId=demo-user-001");
            var successBody = await success.Content.ReadAsStringAsync();
            if (success.StatusCode != HttpStatusCode.OK
                || success.Headers.CacheControl?.ToString() != "no-store"
                || successBody != "{\"userId\":\"demo-user-001\",\"mode\":\"legacy\",\"message\":\"Backend: legacy\"}"
                || successBody.Contains("backend_demo_v2", StringComparison.Ordinal))
                throw new InvalidOperationException("Success response contract failed.");

            Console.WriteLine("HTTP_CONTRACTS_OK");
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"HTTP_CHILD_ERROR={error.GetType().Name}:{error.Message}");
            return 1;
        }
        finally
        {
            Environment.SetEnvironmentVariable(variable, previous);
            await OpenFeature.Api.Instance.ShutdownAsync();
        }
    }

    private sealed class SyntheticWebFactory : WebApplicationFactory<global::Program>
    {
        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.UseEnvironment("Testing");
            builder.ConfigureAppConfiguration((_, configuration) =>
                configuration.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    ["FeatureFlags:ApiUrl"] = "https://flags.synthetic.example/api/v1/",
                    ["FeatureFlags:RefreshSeconds"] = "3600"
                }));
            builder.ConfigureServices(services =>
            {
                services.RemoveAll<IFeatureFlagsHttpClientFactory>();
                services.AddSingleton<IFeatureFlagsHttpClientFactory>(
                    new SyntheticHttpClientFactory());
            });
        }
    }

    private sealed class SyntheticHttpClientFactory : IFeatureFlagsHttpClientFactory
    {
        public HttpClient Create(Uri apiUri, Microsoft.Extensions.Logging.ILogger logger) =>
            new(new EnvironmentDocumentOnlyHandler(apiUri, new DocumentTransport(), logger));
    }

    private sealed class DocumentTransport : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request, CancellationToken cancellationToken)
        {
            const string document = """
            {
              "id": 1, "api_key": "ser.synthetic-test-key", "name": "Synthetic test",
              "project": { "id": 1, "name": "Reference", "hide_disabled_flags": false,
                "segments": [], "organisation": { "id": 1, "name": "Reference",
                  "feature_analytics": false, "persist_trait_data": false,
                  "stop_serving_flags": false } },
              "segment_overrides": [], "identity_overrides": [], "feature_states": [{
                "id": 1, "enabled": false, "feature_state_value": null,
                "multivariate_feature_state_values": [],
                "feature": { "id": 1, "name": "backend_demo_v2", "type": "STANDARD" }
              }]
            }
            """;
            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            { Content = new StringContent(document) });
        }
    }
}