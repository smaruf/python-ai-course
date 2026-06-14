Testing terms and operational procedures often overlap, but they serve very different purposes in the software development lifecycle. To make this easy to parse, we can split these concepts into three distinct buckets: **Testing Types**, **Testing Methodologies**, **and Operational Tools**.

---

## 1. Testing Types (The "What" and "Why")

These terms define *what* aspect of the software you are verifying and *why* you are running the test.

### Feature Test

* **What it is:** Testing a specific, isolated new piece of functionality (a "feature") to ensure it works according to its requirements.
* **Scope:** Narrow. It focuses strictly on the newly added code.
* **Example:** Testing if a newly added "Dark Mode" toggle actually turns the background dark when clicked.

### Integration Test

* **What it is:** Testing how different modules, services, or external systems work together.
* **Scope:** Medium to Broad. It focuses on the interfaces and communication pathways between components.
* **Example:** Verifying that when a user clicks "Buy Now," the frontend correctly talks to the payment gateway, and the payment gateway successfully updates the database.

### Regression Test

* **What it is:** Re-running existing tests to ensure that new code changes or bug fixes haven't accidentally broken existing, previously working functionality.
* **Scope:** Broad. It acts as a safety net for the entire system.
* **Example:** Ensuring that adding the "Dark Mode" feature didn't accidentally break the user's ability to log in.

### Load Test

* **What it is:** Testing the system's performance and stability under a specific, expected volume of traffic or data.
* **Scope:** System-wide. It looks at response times, bottlenecks, and resource utilization.
* **Example:** Simulating 10,000 concurrent users accessing an e-commerce site at the exact same time to see if the server crashes or slows down.

---

## 2. Testing Methodology (The "How")

### Test Automation

* **What it is:** The practice of using software tools to execute tests automatically, compare actual outcomes with predicted outcomes, and report results—all without human intervention.
* **How it relates to the others:** **Test automation is not a *type* of test; it is a *method* of executing tests.** You can automate feature tests, integration tests, regression tests, and load tests.
* **Example:** Writing a script using Selenium or Playwright that automatically opens a browser, logs in, and checks if a page loads, rather than having a QA engineer do it manually every day.

---

## 3. Operational Tools (The "Production Guide")

### Runbook

* **What it is:** A documented, step-by-step guide or checklist that system administrators, DevOps, or Site Reliability Engineers (SREs) follow to routine-manage, troubleshoot, or deploy a system.
* **How it differs from testing:** Testing verifies that the software works. A runbook is a manual or semi-automated guide on **how to operate the software** in the real world—especially when things go wrong.
* **Example:** A "Database Recovery Runbook" that lists the exact command-line steps to restore data from a backup if the primary database fails.

---

## Quick Reference Comparison

| Concept | Primary Goal | When is it used? | Analogy (Building a Car) |
| --- | --- | --- | --- |
| **Feature Test** | Verify a new piece of functionality. | During active development. | Checking if the newly installed radio turns on. |
| **Integration Test** | Verify components work together. | When combining code modules. | Checking if turning the steering wheel actually turns the wheels. |
| **Regression Test** | Ensure old features aren't broken. | Before every major release. | Checking that installing the radio didn't accidentally cut power to the headlights. |
| **Load Test** | Verify performance under stress. | Before major traffic events. | Putting the car on a treadmill at 150 mph to see if the engine overheats. |
| **Test Automation** | Speed up testing and reduce human error. | Continuous integration (CI/CD). | Using a robotic rig to open and slam the car door 10,000 times instead of hiring a person to do it. |
| **Runbook** | Standardize operations and incident response. | Production environment / Live ops. | The mechanic's manual explaining how to change the oil or jumpstart the battery. |

Which of these areas are you looking to implement or optimize in your current workflow?
