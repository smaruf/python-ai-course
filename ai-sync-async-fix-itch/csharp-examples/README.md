# C# Async Examples

This directory contains C# examples demonstrating synchronous vs asynchronous programming patterns, particularly focused on AI integration.

## 📋 Prerequisites

- .NET 6.0 or later
- Visual Studio 2022, VS Code, or any C# IDE

## 🚀 Quick Start

### Option 1: Run individual examples

```bash
# Navigate to an example directory
cd basics/SyncVsAsync

# Build and run
dotnet build
dotnet run
```

### Option 2: Use Visual Studio

1. Open the `.csproj` file in Visual Studio
2. Press F5 to run

## 📁 Directory Structure

### `basics/`
- **SyncVsAsync/** - Demonstrates fundamental differences between sync and async
- **TaskBasics/** - Understanding Tasks and async/await
- **AsyncPatterns/** - Common async patterns in C#

### `problems/`
- **CommonMistakes/** - Common pitfalls when using async/await
- **Deadlocks/** - Understanding and avoiding deadlocks
- **ConfigureAwait/** - When and why to use ConfigureAwait

### `best-practices/`
- **ProperPatterns/** - Recommended async patterns
- **ErrorHandling/** - Error handling in async code
- **Cancellation/** - Proper cancellation token usage

### `ai-integration/`
- **SyncAICalls/** - Synchronous AI API calls
- **AsyncAICalls/** - Asynchronous AI API calls with HttpClient
- **AdvancedPatterns/** - Advanced patterns with rate limiting, retry logic

## 📖 Learning Path

1. Start with `basics/SyncVsAsync` to understand fundamentals
2. Study `basics/TaskBasics` to learn about Tasks
3. Review `problems/CommonMistakes` to avoid pitfalls
4. Practice `best-practices/ProperPatterns`
5. Apply knowledge in `ai-integration` examples

## 💡 Key Concepts

### async/await
- `async` keyword marks a method as asynchronous
- `await` keyword suspends execution until the awaited task completes
- Returns `Task` or `Task<T>` for async methods

### Task vs Thread
- Tasks are lighter weight than threads
- Task represents an ongoing operation, not necessarily a thread
- Multiple tasks can run on a single thread

### ConfigureAwait
- `ConfigureAwait(false)` prevents capturing synchronization context
- Use in library code to avoid potential deadlocks
- Generally not needed in ASP.NET Core applications

## 🔗 Related Resources

- [Microsoft Async/Await Documentation](https://docs.microsoft.com/en-us/dotnet/csharp/async)
- [Task-based Asynchronous Pattern](https://docs.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap)
- [Best Practices in Asynchronous Programming](https://docs.microsoft.com/en-us/archive/msdn-magazine/2013/march/async-await-best-practices-in-asynchronous-programming)
