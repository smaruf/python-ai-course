// AI Gateway — C# client example
// =================================
//
// Shows how to call the AI Gateway REST API from C#.
// Uses only the standard library (System.Net.Http) — no NuGet packages needed.
//
// Requires .NET 6+.
//
// Run:
//   dotnet script Client.cs
//   -- or --
//   dotnet run   (inside a .csproj project)

using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

class GatewayClient
{
    private static readonly HttpClient Http = new();
    private const string GatewayUrl = "http://localhost:8000";

    /// <summary>Send a plain prompt to the gateway.</summary>
    public static async Task<GatewayResponse> QueryAsync(string prompt)
    {
        var body = JsonSerializer.Serialize(new { prompt });
        return await PostAsync<GatewayResponse>("/ai/query", body);
    }

    /// <summary>Send a RAG-augmented prompt to the gateway.</summary>
    public static async Task<GatewayResponse> QueryRagAsync(string prompt, string[] documents)
    {
        var body = JsonSerializer.Serialize(new { prompt, documents });
        return await PostAsync<GatewayResponse>("/ai/query/rag", body);
    }

    /// <summary>Fetch the gateway health status.</summary>
    public static async Task<HealthResponse> HealthAsync()
    {
        var resp = await Http.GetStringAsync(GatewayUrl + "/health");
        return JsonSerializer.Deserialize<HealthResponse>(resp)!;
    }

    // -----------------------------------------------------------------------

    private static async Task<T> PostAsync<T>(string path, string jsonBody)
    {
        var content = new StringContent(jsonBody, Encoding.UTF8, "application/json");
        var resp = await Http.PostAsync(GatewayUrl + path, content);
        resp.EnsureSuccessStatusCode();
        var raw = await resp.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(raw)!;
    }
}

class GatewayResponse
{
    [JsonPropertyName("response")] public string Response { get; set; } = "";
    [JsonPropertyName("backend")]  public string Backend  { get; set; } = "";
    [JsonPropertyName("state")]    public string State    { get; set; } = "";
}

class HealthResponse
{
    [JsonPropertyName("status")]           public string Status          { get; set; } = "";
    [JsonPropertyName("copilot_available")] public bool  CopilotAvailable { get; set; }
    [JsonPropertyName("cloud_available")]   public bool  CloudAvailable   { get; set; }
    [JsonPropertyName("local_available")]   public bool  LocalAvailable   { get; set; }
    [JsonPropertyName("circuit_state")]     public string CircuitState    { get; set; } = "";
}

// Entry point
var result = await GatewayClient.QueryAsync("Explain a circuit breaker pattern in two sentences.");
Console.WriteLine($"[{result.Backend}] {result.Response}");

// RAG query
var docs = new[]
{
    "A circuit breaker monitors calls to a remote service.",
    "When failures exceed a threshold the circuit 'opens' and further calls are blocked.",
    "After a timeout the circuit moves to 'half-open' and allows a trial call.",
};
var ragResult = await GatewayClient.QueryRagAsync("When does a circuit breaker open?", docs);
Console.WriteLine($"[{ragResult.Backend}] {ragResult.Response}");

// Health
var health = await GatewayClient.HealthAsync();
Console.WriteLine($"Gateway: {health.Status} | circuit: {health.CircuitState}");
