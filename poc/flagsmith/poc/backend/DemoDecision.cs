using Microsoft.Extensions.Logging;
using OpenFeature;
using OpenFeature.Model;

public static class DemoDecision
{
    public static async Task<DemoReply> EvaluateAsync(
        DemoUser user, FeatureClient featureClient, ILogger logger)
    {
        var context = EvaluationContext.Builder()
            .SetTargetingKey(user.Id)
            .Set("beta", user.Beta)
            .Build();
        var details = await featureClient.GetBooleanDetailsAsync(
            "backend_demo_v2", false, context);
        if (details.ErrorType != OpenFeature.Constant.ErrorType.None)
            logger.LogWarning("Backend demo flag evaluation failed: {ErrorType}", details.ErrorType);

        return DemoReply.Create(user.Id,
            details.ErrorType == OpenFeature.Constant.ErrorType.None && details.Value);
    }
}