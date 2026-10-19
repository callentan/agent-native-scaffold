using System.Collections;
using System.Text.Json;

public sealed record DemoUser(string Id, string Label, bool Beta);

public sealed class DemoUsers : IReadOnlyList<DemoUser>
{
    private const int ExpectedCount = 20;
    private readonly IReadOnlyList<DemoUser> _users;

    private DemoUsers(IReadOnlyList<DemoUser> users) => _users = users;

    public int Count => _users.Count;
    public DemoUser this[int index] => _users[index];
    public IEnumerator<DemoUser> GetEnumerator() => _users.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    public static DemoUsers Load(string path)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException("A demo-user fixture path is required.", nameof(path));
        if (!File.Exists(path))
            throw new FileNotFoundException("The demo-user fixture is required.", path);

        List<DemoUser?>? users;
        try
        {
            users = JsonSerializer.Deserialize<List<DemoUser?>>(
                File.ReadAllText(path), new JsonSerializerOptions(JsonSerializerDefaults.Web));
        }
        catch (JsonException exception)
        {
            throw new InvalidDataException("The demo-user fixture is not valid JSON.", exception);
        }

        if (users is null || users.Count != ExpectedCount)
            throw new InvalidDataException($"The demo-user fixture must contain exactly {ExpectedCount} users.");

        var identifiers = new HashSet<string>(StringComparer.Ordinal);
        foreach (var user in users)
        {
            if (user is null || string.IsNullOrEmpty(user.Id) || !identifiers.Add(user.Id))
                throw new InvalidDataException("The demo-user fixture contains a duplicate or empty ID.");
        }

        var validated = new List<DemoUser>(ExpectedCount);
        for (var index = 0; index < ExpectedCount; index++)
        {
            var user = users[index];
            var expectedNumber = index + 1;
            var expectedId = $"demo-user-{expectedNumber:000}";
            var expectedLabel = $"User {expectedNumber:000}";
            var expectedBeta = expectedNumber <= 5;

            if (user is null
                || !string.Equals(user.Id, expectedId, StringComparison.Ordinal)
                || !string.Equals(user.Label, expectedLabel, StringComparison.Ordinal)
                || user.Beta != expectedBeta)
                throw new InvalidDataException("The demo-user fixture has an invalid ordered entry.");

            if (validated.Any(existing => string.Equals(existing.Id, user.Id, StringComparison.Ordinal)))
                throw new InvalidDataException("The demo-user fixture contains a duplicate ID.");
            validated.Add(user);
        }

        return new DemoUsers(validated.AsReadOnly());
    }

    public DemoUser? Find(string? id) => id is null
        ? null
        : _users.FirstOrDefault(user => string.Equals(user.Id, id, StringComparison.Ordinal));
}
