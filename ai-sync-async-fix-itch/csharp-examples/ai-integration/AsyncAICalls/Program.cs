using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace AsyncAICalls
{
    /// <summary>
    /// Demonstrates asynchronous AI API calls in C#.
    /// Shows proper patterns for concurrent AI operations.
    /// </summary>
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("🔄 Asynchronous AI API Calls in C#\n");
            Console.WriteLine("This demonstrates async AI integration patterns.");
            Console.WriteLine("Ideal for: concurrent requests, web apps, high throughput\n");

            try
            {
                await ExampleSingleRequest();
                await ExampleConcurrentRequests();
                await ExampleWithSemaphore();
                await ExampleErrorHandling();
                await ExampleCancellation();

                Console.WriteLine("\n" + new string('=', 60));
                Console.WriteLine("✅ All examples completed!");
                Console.WriteLine(new string('=', 60));
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        // ============================================================================
        // EXAMPLE 1: Single Async Request
        // ============================================================================

        static async Task ExampleSingleRequest()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("EXAMPLE 1: Single Asynchronous Request");
            Console.WriteLine(new string('=', 60));

            var client = new AsyncAIClient();
            var prompt = "Explain async/await in C# in one sentence.";

            Console.WriteLine($"\n📝 Prompt: {prompt}");

            var result = await client.GenerateTextAsync(prompt);

            if (result.Success)
            {
                Console.WriteLine($"\n✅ Response: {result.Response}");
                Console.WriteLine($"⏱️  Time: {result.ElapsedMs / 1000.0:F2}s");
            }
            else
            {
                Console.WriteLine($"\n❌ Error: {result.Error}");
            }
        }

        // ============================================================================
        // EXAMPLE 2: Multiple Concurrent Requests
        // ============================================================================

        static async Task ExampleConcurrentRequests()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("EXAMPLE 2: Multiple Concurrent Requests");
            Console.WriteLine(new string('=', 60));

            var client = new AsyncAIClient();

            var prompts = new[]
            {
                "What is C#?",
                "What is async programming?",
                "What is Task in C#?",
                "What is await keyword?",
                "What is TPL?"
            };

            Console.WriteLine($"\n📝 Processing {prompts.Length} prompts concurrently...");

            var sw = Stopwatch.StartNew();

            // Create tasks for all prompts
            var tasks = new List<Task<AIResult>>();
            foreach (var prompt in prompts)
            {
                tasks.Add(client.GenerateTextAsync(prompt));
            }

            // Wait for all to complete
            var results = await Task.WhenAll(tasks);

            sw.Stop();

            // Display results
            for (int i = 0; i < prompts.Length; i++)
            {
                Console.WriteLine($"\n🔄 Request {i + 1}/{prompts.Length}: {prompts[i]}");

                if (results[i].Success)
                {
                    var response = results[i].Response;
                    var display = response.Length > 100 ? response.Substring(0, 100) + "..." : response;
                    Console.WriteLine($"   ✅ {display}");
                    Console.WriteLine($"   ⏱️  {results[i].ElapsedMs / 1000.0:F2}s");
                }
                else
                {
                    Console.WriteLine($"   ❌ Failed: {results[i].Error}");
                }
            }

            var successful = 0;
            var totalRequestTime = 0.0;
            foreach (var result in results)
            {
                if (result.Success)
                {
                    successful++;
                    totalRequestTime += result.ElapsedMs / 1000.0;
                }
            }

            Console.WriteLine($"\n📊 Summary:");
            Console.WriteLine($"   Total time: {sw.ElapsedMilliseconds / 1000.0:F2}s");
            Console.WriteLine($"   Average per request: {sw.ElapsedMilliseconds / (double)prompts.Length / 1000.0:F2}s");
            Console.WriteLine($"   Successful: {successful}/{results.Length}");

            if (totalRequestTime > 0)
            {
                var speedup = totalRequestTime / (sw.ElapsedMilliseconds / 1000.0);
                Console.WriteLine($"\n💡 Speedup: {speedup:F2}x faster than sequential!");
            }
        }

        // ============================================================================
        // EXAMPLE 3: Concurrency Control with SemaphoreSlim
        // ============================================================================

        static async Task ExampleWithSemaphore()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("EXAMPLE 3: Concurrency Control with SemaphoreSlim");
            Console.WriteLine(new string('=', 60));

            var client = new AsyncAIClient();
            var semaphore = new SemaphoreSlim(3); // Max 3 concurrent requests

            var topics = new[]
            {
                "artificial intelligence",
                "machine learning",
                "neural networks",
                "deep learning",
                "natural language processing",
                "computer vision"
            };

            Console.WriteLine($"\n📝 Processing {topics.Length} topics with max 3 concurrent...");

            var sw = Stopwatch.StartNew();

            async Task<AIResult> ProcessWithLimit(string topic, int index)
            {
                await semaphore.WaitAsync();
                try
                {
                    Console.WriteLine($"[{index + 1}/{topics.Length}] Processing: {topic}");
                    var prompt = $"Define {topic} in one sentence.";
                    return await client.GenerateTextAsync(prompt);
                }
                finally
                {
                    semaphore.Release();
                }
            }

            var tasks = new List<Task<AIResult>>();
            for (int i = 0; i < topics.Length; i++)
            {
                tasks.Add(ProcessWithLimit(topics[i], i));
            }

            var results = await Task.WhenAll(tasks);

            sw.Stop();

            var successful = 0;
            foreach (var result in results)
            {
                if (result.Success) successful++;
            }

            Console.WriteLine($"\n📊 Batch Processing Summary:");
            Console.WriteLine($"   Total items: {topics.Length}");
            Console.WriteLine($"   Successful: {successful}");
            Console.WriteLine($"   Failed: {topics.Length - successful}");
            Console.WriteLine($"   Total time: {sw.ElapsedMilliseconds / 1000.0:F2}s");
            Console.WriteLine($"   Average per item: {sw.ElapsedMilliseconds / (double)topics.Length / 1000.0:F2}s");
        }

        // ============================================================================
        // EXAMPLE 4: Error Handling
        // ============================================================================

        static async Task ExampleErrorHandling()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("EXAMPLE 4: Error Handling with Task.WhenAll");
            Console.WriteLine(new string('=', 60));

            var client = new AsyncAIClient();

            var prompts = new[]
            {
                "What is C#?",
                "What is .NET?",
                "What is ASP.NET Core?"
            };

            Console.WriteLine("\n🔄 Processing requests with error handling...");

            var tasks = new List<Task<AIResult>>();
            foreach (var prompt in prompts)
            {
                tasks.Add(client.GenerateTextAsync(prompt));
            }

            // WhenAll doesn't throw until awaited, and only throws first exception
            // But we can access all results
            var results = await Task.WhenAll(tasks);

            Console.WriteLine("\n📊 Results:");
            for (int i = 0; i < prompts.Length; i++)
            {
                if (results[i].Success)
                {
                    Console.WriteLine($"   ✅ Request {i + 1}: Success");
                }
                else
                {
                    Console.WriteLine($"   ❌ Request {i + 1}: {results[i].Error}");
                }
            }
        }

        // ============================================================================
        // EXAMPLE 5: Cancellation Support
        // ============================================================================

        static async Task ExampleCancellation()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("EXAMPLE 5: Cancellation with CancellationToken");
            Console.WriteLine(new string('=', 60));

            var client = new AsyncAIClient();
            using var cts = new CancellationTokenSource();

            // Cancel after 2 seconds
            cts.CancelAfter(TimeSpan.FromSeconds(2));

            Console.WriteLine("\n🔄 Starting long-running operation (will cancel after 2s)...");

            try
            {
                var result = await client.GenerateTextWithCancellationAsync(
                    "Write a very long story about async programming",
                    cts.Token
                );

                if (result.Success)
                {
                    Console.WriteLine($"   ✅ Completed: {result.Response.Substring(0, Math.Min(50, result.Response.Length))}...");
                }
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine("   ⏹️  Operation was cancelled");
            }
        }
    }

    // ============================================================================
    // AI CLIENT IMPLEMENTATION
    // ============================================================================

    public class AIResult
    {
        public bool Success { get; set; }
        public string Response { get; set; } = string.Empty;
        public string Error { get; set; } = string.Empty;
        public long ElapsedMs { get; set; }
    }

    public class AsyncAIClient
    {
        private static readonly HttpClient httpClient = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(30)
        };

        private readonly string baseUrl;

        public AsyncAIClient(string baseUrl = "http://localhost:11434")
        {
            this.baseUrl = baseUrl;
        }

        public async Task<AIResult> GenerateTextAsync(string prompt, string model = "llama3.1:8b")
        {
            var sw = Stopwatch.StartNew();

            try
            {
                // Simulate API call with delay
                await Task.Delay(Random.Shared.Next(500, 1500));

                // In real implementation, you would call actual API:
                // var response = await CallOllamaAsync(prompt, model);

                var mockResponse = $"This is a simulated response to: {prompt.Substring(0, Math.Min(30, prompt.Length))}...";

                sw.Stop();

                return new AIResult
                {
                    Success = true,
                    Response = mockResponse,
                    ElapsedMs = sw.ElapsedMilliseconds
                };
            }
            catch (Exception ex)
            {
                sw.Stop();

                return new AIResult
                {
                    Success = false,
                    Error = ex.Message,
                    ElapsedMs = sw.ElapsedMilliseconds
                };
            }
        }

        public async Task<AIResult> GenerateTextWithCancellationAsync(
            string prompt,
            CancellationToken cancellationToken,
            string model = "llama3.1:8b")
        {
            var sw = Stopwatch.StartNew();

            try
            {
                // Simulate long-running operation
                for (int i = 0; i < 10; i++)
                {
                    await Task.Delay(500, cancellationToken);
                    Console.WriteLine($"   Working... {i + 1}/10");
                }

                sw.Stop();

                return new AIResult
                {
                    Success = true,
                    Response = $"Response to: {prompt}",
                    ElapsedMs = sw.ElapsedMilliseconds
                };
            }
            catch (OperationCanceledException)
            {
                sw.Stop();
                throw;
            }
            catch (Exception ex)
            {
                sw.Stop();

                return new AIResult
                {
                    Success = false,
                    Error = ex.Message,
                    ElapsedMs = sw.ElapsedMilliseconds
                };
            }
        }

        // Example of actual Ollama API call (commented out)
        /*
        private async Task<string> CallOllamaAsync(string prompt, string model)
        {
            var url = $"{baseUrl}/api/generate";

            var payload = new
            {
                model = model,
                prompt = prompt,
                stream = false
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<JsonElement>(json);

            return result.GetProperty("response").GetString() ?? string.Empty;
        }
        */
    }
}
