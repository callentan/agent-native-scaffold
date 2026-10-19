using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;

public static class ServerKeyConfiguration
{
    public static IConfiguration Load(
        IHostEnvironment environment, IConfiguration? userSecretsOverride = null)
    {
        var builder = new ConfigurationBuilder()
            .SetBasePath(environment.ContentRootPath);
        if (userSecretsOverride is null)
            builder.AddUserSecrets<Program>(optional: true);
        else
            builder.AddConfiguration(userSecretsOverride);
        return builder.AddEnvironmentVariables().Build();
    }

    public static string Require(IConfiguration configuration)
    {
        var key = configuration["FeatureFlags:EnvironmentKey"];
        if (string.IsNullOrWhiteSpace(key)
            || !key.StartsWith("ser.", StringComparison.Ordinal)
            || key.Any(char.IsWhiteSpace))
            throw new InvalidOperationException(
                "FeatureFlags:EnvironmentKey must be a server-side key from user-secrets or environment.");
        return key;
    }
}