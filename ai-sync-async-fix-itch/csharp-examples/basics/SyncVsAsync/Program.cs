using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;

namespace SyncVsAsync
{
    /// <summary>
    /// Demonstrates the fundamental differences between synchronous and asynchronous execution in C#.
    /// </summary>
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("🔄 Synchronous vs Asynchronous Programming in C#\n");
            Console.WriteLine("This example demonstrates the fundamental differences");
            Console.WriteLine("between sync and async execution patterns.\n");

            // Run all demonstrations
            DemoSynchronous();
            await DemoAsynchronous();
            await ComparePerformance();
            DemoCpuBound();
            await DemoIoBound();

            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("✅ All demonstrations completed!");
            Console.WriteLine(new string('=', 60));
        }

        // ============================================================================
        // SYNCHRONOUS APPROACH
        // ============================================================================

        static void DemoSynchronous()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("SYNCHRONOUS EXECUTION");
            Console.WriteLine(new string('=', 60));

            var sw = Stopwatch.StartNew();

            // Each operation blocks until complete
            var result1 = FetchDataSync("API-1", 2000);
            var result2 = FetchDataSync("API-2", 2000);
            var result3 = FetchDataSync("API-3", 2000);

            sw.Stop();

            Console.WriteLine($"\n✅ Completed in {sw.ElapsedMilliseconds / 1000.0:F2} seconds");
            Console.WriteLine($"📊 Total wait time: 6.0 seconds (2 + 2 + 2)");
        }

        static string FetchDataSync(string source, int delayMs)
        {
            Console.WriteLine($"[SYNC] Starting fetch from {source}...");
            Thread.Sleep(delayMs); // Blocking operation
            Console.WriteLine($"[SYNC] Completed fetch from {source}");
            return $"Data from {source}";
        }

        // ============================================================================
        // ASYNCHRONOUS APPROACH
        // ============================================================================

        static async Task DemoAsynchronous()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("ASYNCHRONOUS EXECUTION");
            Console.WriteLine(new string('=', 60));

            var sw = Stopwatch.StartNew();

            // All operations run concurrently
            var task1 = FetchDataAsync("API-1", 2000);
            var task2 = FetchDataAsync("API-2", 2000);
            var task3 = FetchDataAsync("API-3", 2000);

            var results = await Task.WhenAll(task1, task2, task3);

            sw.Stop();

            Console.WriteLine($"\n✅ Completed in {sw.ElapsedMilliseconds / 1000.0:F2} seconds");
            Console.WriteLine($"📊 Total wait time: ~2.0 seconds (max of concurrent operations)");
        }

        static async Task<string> FetchDataAsync(string source, int delayMs)
        {
            Console.WriteLine($"[ASYNC] Starting fetch from {source}...");
            await Task.Delay(delayMs); // Non-blocking operation
            Console.WriteLine($"[ASYNC] Completed fetch from {source}");
            return $"Data from {source}";
        }

        // ============================================================================
        // PERFORMANCE COMPARISON
        // ============================================================================

        static async Task ComparePerformance()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("PERFORMANCE COMPARISON");
            Console.WriteLine(new string('=', 60));

            // Measure synchronous
            var syncSw = Stopwatch.StartNew();
            FetchDataSync("Test-1", 1000);
            FetchDataSync("Test-2", 1000);
            FetchDataSync("Test-3", 1000);
            syncSw.Stop();
            var syncTime = syncSw.ElapsedMilliseconds / 1000.0;

            // Measure asynchronous
            var asyncSw = Stopwatch.StartNew();
            await Task.WhenAll(
                FetchDataAsync("Test-4", 1000),
                FetchDataAsync("Test-5", 1000),
                FetchDataAsync("Test-6", 1000)
            );
            asyncSw.Stop();
            var asyncTime = asyncSw.ElapsedMilliseconds / 1000.0;

            Console.WriteLine($"\nSynchronous:  {syncTime:F2}s  ⏳ (Sequential)");
            Console.WriteLine($"Asynchronous: {asyncTime:F2}s  ⚡ (Concurrent)");
            Console.WriteLine($"Speedup:      {syncTime / asyncTime:F2}x  🚀");

            // Visual representation
            Console.WriteLine("\n📊 Visual Timeline:");
            Console.WriteLine("\nSynchronous (Sequential):");
            Console.WriteLine("API-1 ████████ (1s)");
            Console.WriteLine("                API-2 ████████ (1s)");
            Console.WriteLine("                                API-3 ████████ (1s)");
            Console.WriteLine("Total: ~3 seconds");

            Console.WriteLine("\nAsynchronous (Concurrent):");
            Console.WriteLine("API-1 ████████ (1s)");
            Console.WriteLine("API-2 ████████ (1s)");
            Console.WriteLine("API-3 ████████ (1s)");
            Console.WriteLine("Total: ~1 second");
        }

        // ============================================================================
        // CPU-BOUND OPERATIONS
        // ============================================================================

        static void DemoCpuBound()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("CPU-BOUND OPERATIONS (Better with Sync)");
            Console.WriteLine(new string('=', 60));

            var sw = Stopwatch.StartNew();
            var result = CalculateFibonacci(35);
            sw.Stop();

            Console.WriteLine($"Fibonacci(35) = {result}");
            Console.WriteLine($"Time: {sw.ElapsedMilliseconds / 1000.0:F2}s");
            Console.WriteLine("\n💡 CPU-bound tasks don't benefit from async");
            Console.WriteLine("   because they're not waiting for I/O");
        }

        static long CalculateFibonacci(int n)
        {
            if (n <= 1) return n;
            return CalculateFibonacci(n - 1) + CalculateFibonacci(n - 2);
        }

        // ============================================================================
        // I/O-BOUND OPERATIONS
        // ============================================================================

        static async Task DemoIoBound()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("I/O-BOUND OPERATIONS (Better with Async)");
            Console.WriteLine(new string('=', 60));

            var sw = Stopwatch.StartNew();

            // Make 5 concurrent "API calls"
            var tasks = new[]
            {
                SimulatedApiCall(1, 1000),
                SimulatedApiCall(2, 1500),
                SimulatedApiCall(3, 800),
                SimulatedApiCall(4, 1200),
                SimulatedApiCall(5, 900)
            };

            var results = await Task.WhenAll(tasks);

            sw.Stop();

            Console.WriteLine($"\nMade 5 API calls in {sw.ElapsedMilliseconds / 1000.0:F2}s");
            Console.WriteLine("Sequential would take: 5.4s (1.0 + 1.5 + 0.8 + 1.2 + 0.9)");
            Console.WriteLine($"Async took: {sw.ElapsedMilliseconds / 1000.0:F2}s (max = 1.5s)");
            Console.WriteLine($"Speedup: {5.4 / (sw.ElapsedMilliseconds / 1000.0):F2}x");

            Console.WriteLine("\n💡 Key Takeaways:");
            Console.WriteLine("1. Sync blocks execution - each operation waits for previous");
            Console.WriteLine("2. Async allows concurrent execution - operations run together");
            Console.WriteLine("3. For I/O-bound tasks, async can be significantly faster");
            Console.WriteLine("4. Async is ideal for API calls, database queries, file I/O");
        }

        static async Task<string> SimulatedApiCall(int apiId, int delayMs)
        {
            await Task.Delay(delayMs);
            return $"Response from API {apiId}";
        }
    }
}
