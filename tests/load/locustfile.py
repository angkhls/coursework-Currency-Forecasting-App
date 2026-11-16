from locust import HttpUser, between, task


class CurrencyAppUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(4)
    def view_dashboard(self):
        self.client.get("/api/v1/dashboard", name="/api/v1/dashboard")

    @task(3)
    def convert_currency(self):
        self.client.get("/api/v1/convert?amount=100&from=USD&to=EUR", name="/api/v1/convert")

    @task(2)
    def view_chart(self):
        self.client.get("/api/v1/pairs/USD_BYN/chart?period=month", name="/api/v1/pairs/{pair}/chart")

    @task(1)
    def view_forecast(self):
        self.client.get("/api/v1/pairs/USD_BYN/forecast?days=7&method=sarimax", name="/api/v1/pairs/{pair}/forecast")
