public sealed record DemoReply(string UserId, string Mode, string Message)
{
    public static DemoReply Create(string userId, bool enabled) =>
        new(userId, enabled ? "new" : "legacy",
            enabled ? "Backend: new" : "Backend: legacy");
}