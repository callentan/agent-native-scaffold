using Xunit;

public sealed class DemoUsersTests
{
    [Fact]
    public void LoadsTheExactSyntheticFixture()
    {
        var users = DemoUsers.Load(Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "shared", "demo-users.json")));

        Assert.Equal(20, users.Count);
        Assert.Equal(5, users.Count(user => user.Beta));
        Assert.Equal("demo-user-001", users[0].Id);
        Assert.Equal("User 020", users[^1].Label);
        Assert.Null(users.Find("demo-user-001 "));
        Assert.Null(users.Find("unknown"));
    }

    [Fact]
    public void RejectsDuplicateOrMalformedFixtureEntries()
    {
        var file = Path.GetTempFileName();
        try
        {
            File.WriteAllText(file, "[{\"id\":\"demo-user-001\",\"label\":\"User 001\",\"beta\":true},{\"id\":\"demo-user-001\",\"label\":\"User 001\",\"beta\":true}]");
            Assert.Throws<InvalidDataException>(() => DemoUsers.Load(file));
        }
        finally
        {
            File.Delete(file);
        }
    }
}