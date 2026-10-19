using Xunit;

public sealed class DemoReplyTests
{
    [Theory]
    [InlineData(false, "legacy", "Backend: legacy")]
    [InlineData(true, "new", "Backend: new")]
    public void MapsTheEvaluatedBranch(bool enabled, string mode, string message)
    {
        var reply = DemoReply.Create("demo-user-001", enabled);
        Assert.Equal("demo-user-001", reply.UserId);
        Assert.Equal(mode, reply.Mode);
        Assert.Equal(message, reply.Message);
    }
}