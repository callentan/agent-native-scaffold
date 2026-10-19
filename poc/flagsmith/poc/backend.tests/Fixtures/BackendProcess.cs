using System.Diagnostics;
using System.Net.Http;

namespace Fixtures;

/// <summary>
/// Owns one backend process so native Flagsmith polling cannot leak across hosts in a test process.
/// </summary>
public sealed class BackendProcess : IAsyncDisposable
{
    private readonly Process _process;
    private readonly Task<string> _standardOutput;
    private readonly Task<string> _standardError;
    private int _disposed;
    private static int _activeProcessCount;

    private BackendProcess(Process process)
    {
        _process = process;
        _standardOutput = process.StandardOutput.ReadToEndAsync();
        _standardError = process.StandardError.ReadToEndAsync();
    }

    public static int ActiveProcessCount => Volatile.Read(ref _activeProcessCount);
    public int ProcessId => _process.Id;
    public int ExitCode => _process.ExitCode;
    public string StandardOutput => _standardOutput.GetAwaiter().GetResult();
    public string StandardError => _standardError.GetAwaiter().GetResult();

    public static async Task<BackendProcess> StartAsync(
        string assemblyPath,
        string workingDirectory,
        Uri readinessUri,
        TimeSpan readinessTimeout,
        IReadOnlyDictionary<string, string?>? environment = null)
    {
        if (!readinessUri.IsAbsoluteUri
            || (readinessUri.Scheme != Uri.UriSchemeHttp
                && readinessUri.Scheme != Uri.UriSchemeHttps))
            throw new ArgumentException("A bounded absolute HTTP(S) readiness URI is required.",
                nameof(readinessUri));
        if (readinessTimeout <= TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(readinessTimeout));

        var owned = await StartCommandAsync(assemblyPath, workingDirectory, [], environment);
        using var http = new HttpClient { Timeout = TimeSpan.FromMilliseconds(500) };
        var deadline = DateTimeOffset.UtcNow + readinessTimeout;
        while (DateTimeOffset.UtcNow < deadline)
        {
            if (owned._process.HasExited)
            {
                var exitCode = owned._process.ExitCode;
                var error = await owned._standardError;
                await owned.DisposeAsync();
                throw new InvalidOperationException(
                    $"The backend exited before readiness with code {exitCode}. stderr: {error}");
            }

            try
            {
                using var response = await http.GetAsync(readinessUri);
                if (response.IsSuccessStatusCode)
                    return owned;
            }
            catch (HttpRequestException)
            {
                // The bounded loop handles startup races without retrying application work.
            }
            catch (TaskCanceledException)
            {
                // The readiness probe has its own short timeout.
            }

            await Task.Delay(TimeSpan.FromMilliseconds(50));
        }

        await owned.DisposeAsync();
        throw new TimeoutException(
            $"The backend did not become ready within {readinessTimeout}. stderr: {owned.StandardError}");
    }

    public static Task<BackendProcess> StartCommandAsync(
        string assemblyPath,
        string workingDirectory,
        IReadOnlyList<string> arguments,
        IReadOnlyDictionary<string, string?>? environment = null)
    {
        if (!File.Exists(assemblyPath))
            throw new FileNotFoundException("The backend assembly is required.", assemblyPath);
        if (!Directory.Exists(workingDirectory))
            throw new DirectoryNotFoundException(workingDirectory);

        var startInfo = new ProcessStartInfo
        {
            FileName = "dotnet",
            WorkingDirectory = Path.GetFullPath(workingDirectory),
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };
        startInfo.ArgumentList.Add(Path.GetFullPath(assemblyPath));
        foreach (var argument in arguments)
            startInfo.ArgumentList.Add(argument);
        if (environment is not null)
        {
            foreach (var item in environment)
                startInfo.Environment[item.Key] = item.Value;
        }

        var process = new Process { StartInfo = startInfo };
        if (!process.Start())
        {
            process.Dispose();
            throw new InvalidOperationException("The backend process could not be started.");
        }

        Interlocked.Increment(ref _activeProcessCount);
        return Task.FromResult(new BackendProcess(process));
    }

    public async Task WaitForSuccessfulExitAsync()
    {
        await WaitForExitAsync(TimeSpan.FromMinutes(1));
        if (ExitCode != 0)
            throw new InvalidOperationException(
                $"The backend exited with code {ExitCode}. stderr: {StandardError}");
    }

    public async Task WaitForExitAsync(TimeSpan timeout)
    {
        if (timeout <= TimeSpan.Zero)
            throw new ArgumentOutOfRangeException(nameof(timeout));
        var exit = _process.WaitForExitAsync();
        if (await Task.WhenAny(exit, Task.Delay(timeout)) != exit)
            throw new TimeoutException($"The child process did not exit within {timeout}.");
        await exit;
        await Task.WhenAll(_standardOutput, _standardError);
    }

    public async ValueTask DisposeAsync()
    {
        if (Interlocked.Exchange(ref _disposed, 1) != 0)
            return;
        try
        {
            if (!_process.HasExited)
                _process.Kill(entireProcessTree: true);
            await _process.WaitForExitAsync();
            await Task.WhenAll(_standardOutput, _standardError);
        }
        catch (InvalidOperationException)
        {
            // The process handle may already have been released after a failed start/exit path.
        }
        finally
        {
            Interlocked.Decrement(ref _activeProcessCount);
            _process.Dispose();
        }
    }
}
