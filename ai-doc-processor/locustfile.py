from locust import HttpUser, task, between


class DocumentUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    @task(1)
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def upload_and_stream(self):
        sample = b"This is a synthetic load-test document. " * 50
        files = {"file": ("load_test.txt", sample, "text/plain")}
        with self.client.post(
            "/api/documents/upload",
            files=files,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status {response.status_code}")
