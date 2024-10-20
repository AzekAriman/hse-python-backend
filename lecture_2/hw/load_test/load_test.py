# lecture_2/hw/load_test/load_test.py

from locust import HttpUser, task, between, events
from prometheus_client import start_http_server, Summary, Counter, Gauge
import time
import threading

# Метрики Prometheus
REQUEST_TIME = Summary('locust_request_processing_seconds', 'Time spent processing request')
REQUEST_COUNT = Counter('locust_request_count', 'Total number of requests')
SUCCESS_REQUEST_COUNT = Counter('locust_success_request_count', 'Total number of successful requests')
FAILURE_REQUEST_COUNT = Counter('locust_failure_request_count', 'Total number of failed requests')
USER_COUNT = Gauge('locust_user_count', 'Current number of users')

# Функция для запуска Prometheus сервера
def start_prometheus_exporter():
    start_http_server(8001)

# Запуск Prometheus сервера в отдельном потоке
threading.Thread(target=start_prometheus_exporter, daemon=True).start()

class LoadTestUser(HttpUser):
    wait_time = between(0.9, 1.1)  # Пауза между запросами от 0.9 до 1.1 секунд

    @task
    def create_cart(self):
        start_time = time.time()
        with self.client.post("/cart", catch_response=True) as response:
            duration = time.time() - start_time
            REQUEST_TIME.observe(duration)
            REQUEST_COUNT.inc()
            USER_COUNT.set(self.environment.runner.user_count)
            if response.status_code == 201:
                SUCCESS_REQUEST_COUNT.inc()
            else:
                FAILURE_REQUEST_COUNT.inc()
                response.failure(f"Failed with status code {response.status_code}")

# Функция для остановки теста через 10 минут
def stop_test():
    time.sleep(600)  # 600 секунд = 10 минут
    events.quitting.fire()
    print("Test completed.")

# Запуск функции остановки теста в отдельном потоке
threading.Thread(target=stop_test, daemon=True).start()
