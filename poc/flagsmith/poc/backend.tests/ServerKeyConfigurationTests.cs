using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Xunit;

public sealed class ServerKeyConfigurationTests
{
    [Fact]
    public void AppSettingsAndCommandLineKeysAreIgnored()
    {
        var root = Directory.CreateTempSubdirectory();
        const string variable = "FeatureFlags__EnvironmentKey";
        var previous = Environment.GetEnvironmentVariable(variable);
        try
        {
            File.WriteAllText(Path.Combine(root.FullName, "appsettings.json"),
                "{\"FeatureFlags\":{\"EnvironmentKey\":\"ser.appsettings-only\"}}");
            Environment.SetEnvironmentVariable(variable, null);
            var builder = WebApplication.CreateBuilder(new WebApplicationOptions
            {
                ContentRootPath = root.FullName,
                Args = ["--FeatureFlags:EnvironmentKey=ser.commandline-only"]
            });

            Assert.Equal("ser.commandline-only", builder.Configuration["FeatureFlags:EnvironmentKey"]);
            var emptyUserSecrets = new ConfigurationBuilder().Build();
            var secretsAndEnvironment = ServerKeyConfiguration.Load(
                builder.Environment, emptyUserSecrets);
            Assert.Null(secretsAndEnvironment["FeatureFlags:EnvironmentKey"]);
            Assert.Throws<InvalidOperationException>(() =>
                ServerKeyConfiguration.Require(secretsAndEnvironment));
        }
        finally
        {
            Environment.SetEnvironmentVariable(variable, previous);
            root.Delete(recursive: true);
        }
    }

    [Fact]
    public void EnvironmentKeyIsAcceptedWithoutLoggingOrDisplayingIt()
    {
        const string variable = "FeatureFlags__EnvironmentKey";
        const string syntheticKey = "ser.synthetic-approved-source";
        var previous = Environment.GetEnvironmentVariable(variable);
        try
        {
            Environment.SetEnvironmentVariable(variable, syntheticKey);
            var builder = WebApplication.CreateBuilder(new WebApplicationOptions
            {
                ContentRootPath = Directory.GetCurrentDirectory()
            });
            Assert.Equal(syntheticKey,
                ServerKeyConfiguration.Require(ServerKeyConfiguration.Load(builder.Environment)));
        }
        finally
        {
            Environment.SetEnvironmentVariable(variable, previous);
        }
    }

    [Fact]
    public void UserSecretShapedConfigurationIsAcceptedByTheKeyValidator()
    {
        var configuration = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?>
            {
                ["FeatureFlags:EnvironmentKey"] = "ser.synthetic-user-secret"
            })
            .Build();

        Assert.Equal("ser.synthetic-user-secret", ServerKeyConfiguration.Require(configuration));
    }
}