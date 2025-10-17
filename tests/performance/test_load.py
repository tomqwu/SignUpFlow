"""
Performance and load tests.

Tests application performance under various load conditions:
- Response time under load
- Concurrent user handling
- Database query performance
- Solver performance with large datasets
- Memory usage
- API throughput
"""

import pytest
import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


API_BASE_URL = "http://localhost:8000/api"


class TestResponseTimePerformance:
    """Test response times for critical endpoints."""

    def test_login_response_time(self):
        """
        Test login endpoint responds quickly.

        Performance Target: < 500ms for login
        """
        # Create test user
        org_id = f"org_perf_login_{int(time.time())}"
        user_email = f"perf_login_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Perf Login Org"
        })

        requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": user_email,
            "password": "Test123!",
            "name": "Perf User",
            "org_id": org_id
        })

        # Measure login response time
        start_time = time.time()
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": user_email,
            "password": "Test123!"
        })
        end_time = time.time()

        assert response.status_code == 200

        response_time_ms = (end_time - start_time) * 1000
        print(f"\n📊 Login response time: {response_time_ms:.2f}ms")

        # Performance target: < 500ms
        assert response_time_ms < 500, f"Login too slow: {response_time_ms:.2f}ms"

    def test_get_people_response_time(self):
        """
        Test GET /people endpoint responds quickly.

        Performance Target: < 200ms for listing people
        """
        # Create test org and users
        org_id = f"org_perf_people_{int(time.time())}"
        user_email = f"perf_people_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Perf People Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": user_email,
            "password": "Test123!",
            "name": "Perf User",
            "org_id": org_id,
            "roles": ["admin"]
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Add 10 people to org
        for i in range(10):
            requests.post(f"{API_BASE_URL}/auth/signup", json={
                "email": f"person{i}_{int(time.time())}@test.com",
                "password": "Test123!",
                "name": f"Person {i}",
                "org_id": org_id
            })

        # Measure GET /people response time
        start_time = time.time()
        response = requests.get(
            f"{API_BASE_URL}/people/?org_id={org_id}",
            headers=headers
        )
        end_time = time.time()

        assert response.status_code == 200

        response_time_ms = (end_time - start_time) * 1000
        print(f"\n📊 GET /people response time: {response_time_ms:.2f}ms")

        # Performance target: < 200ms
        assert response_time_ms < 200, f"GET /people too slow: {response_time_ms:.2f}ms"

    def test_get_events_response_time(self):
        """
        Test GET /events endpoint responds quickly.

        Performance Target: < 200ms for listing events
        """
        # Create test org and events
        org_id = f"org_perf_events_{int(time.time())}"
        user_email = f"perf_events_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Perf Events Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": user_email,
            "password": "Test123!",
            "name": "Perf User",
            "org_id": org_id,
            "roles": ["admin"]
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Create 20 events
        for i in range(20):
            event_time = (datetime.now() + timedelta(days=i)).isoformat()
            requests.post(
                f"{API_BASE_URL}/events?org_id={org_id}",
                json={
                    "id": f"event_{i}_{int(time.time())}",
                    "org_id": org_id,
                    "type": f"Service {i}",
                    "start_time": event_time,
                    "end_time": (datetime.now() + timedelta(days=i, hours=2)).isoformat(),
                },
                headers=headers
            )

        # Measure GET /events response time
        start_time = time.time()
        response = requests.get(
            f"{API_BASE_URL}/events/?org_id={org_id}",
            headers=headers
        )
        end_time = time.time()

        assert response.status_code == 200

        response_time_ms = (end_time - start_time) * 1000
        print(f"\n📊 GET /events response time: {response_time_ms:.2f}ms")

        # Performance target: < 200ms
        assert response_time_ms < 200, f"GET /events too slow: {response_time_ms:.2f}ms"


class TestConcurrentUsers:
    """Test application handles concurrent users."""

    def test_concurrent_logins(self):
        """
        Test handling 10 concurrent login requests.

        Performance Target: All complete in < 5 seconds
        """
        # Create test org and users
        org_id = f"org_perf_concurrent_{int(time.time())}"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Perf Concurrent Org"
        })

        # Create 10 test users
        user_credentials = []
        for i in range(10):
            email = f"concurrent{i}_{int(time.time())}@test.com"
            password = "Test123!"

            requests.post(f"{API_BASE_URL}/auth/signup", json={
                "email": email,
                "password": password,
                "name": f"Concurrent User {i}",
                "org_id": org_id
            })

            user_credentials.append((email, password))

        # Login all users concurrently
        def login_user(credentials):
            email, password = credentials
            start = time.time()
            response = requests.post(f"{API_BASE_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            end = time.time()
            return response.status_code, (end - start) * 1000

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(login_user, creds) for creds in user_credentials]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()

        # All logins should succeed
        assert all(status == 200 for status, _ in results)

        # Calculate statistics
        response_times = [rt for _, rt in results]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        total_time = (end_time - start_time) * 1000

        print(f"\n📊 Concurrent logins (10 users):")
        print(f"   Total time: {total_time:.2f}ms")
        print(f"   Avg response: {avg_response_time:.2f}ms")
        print(f"   Max response: {max_response_time:.2f}ms")

        # Performance target: < 5 seconds total
        assert total_time < 5000, f"Concurrent logins too slow: {total_time:.2f}ms"

    def test_concurrent_api_reads(self):
        """
        Test handling 20 concurrent GET requests.

        Performance Target: All complete in < 3 seconds
        """
        # Create test org
        org_id = f"org_perf_reads_{int(time.time())}"
        user_email = f"perf_reads_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Perf Reads Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": user_email,
            "password": "Test123!",
            "name": "Perf User",
            "org_id": org_id
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Make 20 concurrent GET /people requests
        def get_people():
            start = time.time()
            response = requests.get(
                f"{API_BASE_URL}/people/?org_id={org_id}",
                headers=headers
            )
            end = time.time()
            return response.status_code, (end - start) * 1000

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(get_people) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()

        # All requests should succeed
        assert all(status == 200 for status, _ in results)

        # Calculate statistics
        response_times = [rt for _, rt in results]
        avg_response_time = statistics.mean(response_times)
        total_time = (end_time - start_time) * 1000

        print(f"\n📊 Concurrent GET requests (20):")
        print(f"   Total time: {total_time:.2f}ms")
        print(f"   Avg response: {avg_response_time:.2f}ms")

        # Performance target: < 3 seconds total
        assert total_time < 3000, f"Concurrent reads too slow: {total_time:.2f}ms"


class TestSolverPerformance:
    """Test constraint solver performance with various dataset sizes."""

    def test_solver_small_dataset(self):
        """
        Test solver with small dataset (5 people, 2 events).

        Performance Target: < 1 second
        """
        # Create test org
        org_id = f"org_solver_small_{int(time.time())}"
        admin_email = f"solver_small_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Solver Small Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": admin_email,
            "password": "Test123!",
            "name": "Solver Admin",
            "org_id": org_id,
            "roles": ["admin"]
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Create 5 people
        for i in range(5):
            requests.post(f"{API_BASE_URL}/auth/signup", json={
                "email": f"solver_person{i}_{int(time.time())}@test.com",
                "password": "Test123!",
                "name": f"Person {i}",
                "org_id": org_id
            })

        # Create 2 events
        for i in range(2):
            event_time = (datetime.now() + timedelta(days=i)).isoformat()
            requests.post(
                f"{API_BASE_URL}/events?org_id={org_id}",
                json={
                    "id": f"event_{i}_{int(time.time())}",
                    "org_id": org_id,
                    "type": f"Service {i}",
                    "start_time": event_time,
                    "end_time": (datetime.now() + timedelta(days=i, hours=2)).isoformat(),
                    "role_requirements": {"usher": 2}
                },
                headers=headers
            )

        # Run solver
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/solver/solve",
            json={"org_id": org_id},
            headers=headers
        )
        end_time = time.time()

        # Solver should succeed or return valid response
        assert response.status_code in [200, 201]

        solver_time_ms = (end_time - start_time) * 1000
        print(f"\n📊 Solver (5 people, 2 events): {solver_time_ms:.2f}ms")

        # Performance target: < 1 second
        assert solver_time_ms < 1000, f"Solver too slow: {solver_time_ms:.2f}ms"

    def test_solver_medium_dataset(self):
        """
        Test solver with medium dataset (20 people, 10 events).

        Performance Target: < 5 seconds
        """
        # Create test org
        org_id = f"org_solver_medium_{int(time.time())}"
        admin_email = f"solver_medium_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Solver Medium Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": admin_email,
            "password": "Test123!",
            "name": "Solver Admin",
            "org_id": org_id,
            "roles": ["admin"]
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Create 20 people
        for i in range(20):
            requests.post(f"{API_BASE_URL}/auth/signup", json={
                "email": f"solver_person{i}_{int(time.time())}@test.com",
                "password": "Test123!",
                "name": f"Person {i}",
                "org_id": org_id
            })

        # Create 10 events
        for i in range(10):
            event_time = (datetime.now() + timedelta(days=i)).isoformat()
            requests.post(
                f"{API_BASE_URL}/events?org_id={org_id}",
                json={
                    "id": f"event_{i}_{int(time.time())}",
                    "org_id": org_id,
                    "type": f"Service {i}",
                    "start_time": event_time,
                    "end_time": (datetime.now() + timedelta(days=i, hours=2)).isoformat(),
                    "role_requirements": {"usher": 2, "greeter": 1}
                },
                headers=headers
            )

        # Run solver
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/solver/solve",
            json={"org_id": org_id},
            headers=headers
        )
        end_time = time.time()

        # Solver should succeed or return valid response
        assert response.status_code in [200, 201]

        solver_time_ms = (end_time - start_time) * 1000
        print(f"\n📊 Solver (20 people, 10 events): {solver_time_ms:.2f}ms")

        # Performance target: < 5 seconds
        assert solver_time_ms < 5000, f"Solver too slow: {solver_time_ms:.2f}ms"

    @pytest.mark.slow
    def test_solver_large_dataset(self):
        """
        Test solver with large dataset (100 people, 50 events).

        Performance Target: < 30 seconds
        Warning: This test is slow and marked with @pytest.mark.slow
        Run with: pytest -v -m slow
        """
        # Create test org
        org_id = f"org_solver_large_{int(time.time())}"
        admin_email = f"solver_large_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Solver Large Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": admin_email,
            "password": "Test123!",
            "name": "Solver Admin",
            "org_id": org_id,
            "roles": ["admin"]
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Create 100 people (this will take a while)
        print("\n📊 Creating 100 people...")
        for i in range(100):
            requests.post(f"{API_BASE_URL}/auth/signup", json={
                "email": f"solver_person{i}_{int(time.time())}@test.com",
                "password": "Test123!",
                "name": f"Person {i}",
                "org_id": org_id
            })

        # Create 50 events
        print("📊 Creating 50 events...")
        for i in range(50):
            event_time = (datetime.now() + timedelta(days=i)).isoformat()
            requests.post(
                f"{API_BASE_URL}/events?org_id={org_id}",
                json={
                    "id": f"event_{i}_{int(time.time())}",
                    "org_id": org_id,
                    "type": f"Service {i}",
                    "start_time": event_time,
                    "end_time": (datetime.now() + timedelta(days=i, hours=2)).isoformat(),
                    "role_requirements": {"usher": 2, "greeter": 1, "tech": 1}
                },
                headers=headers
            )

        # Run solver
        print("📊 Running solver...")
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/solver/solve",
            json={"org_id": org_id},
            headers=headers,
            timeout=60  # 60 second timeout
        )
        end_time = time.time()

        # Solver should succeed or return valid response
        assert response.status_code in [200, 201]

        solver_time_seconds = end_time - start_time
        print(f"\n📊 Solver (100 people, 50 events): {solver_time_seconds:.2f}s")

        # Performance target: < 30 seconds
        assert solver_time_seconds < 30, f"Solver too slow: {solver_time_seconds:.2f}s"


class TestDatabasePerformance:
    """Test database query performance."""

    def test_bulk_insert_performance(self):
        """
        Test bulk insertion of 100 people.

        Performance Target: < 10 seconds for 100 inserts
        """
        org_id = f"org_bulk_{int(time.time())}"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Bulk Insert Org"
        })

        # Insert 100 people
        start_time = time.time()

        for i in range(100):
            requests.post(f"{API_BASE_URL}/auth/signup", json={
                "email": f"bulk_person{i}_{int(time.time())}@test.com",
                "password": "Test123!",
                "name": f"Person {i}",
                "org_id": org_id
            })

        end_time = time.time()

        insert_time_seconds = end_time - start_time
        print(f"\n📊 Bulk insert (100 people): {insert_time_seconds:.2f}s")

        # Performance target: < 10 seconds
        assert insert_time_seconds < 10, f"Bulk insert too slow: {insert_time_seconds:.2f}s"


class TestAPIThroughput:
    """Test API request throughput."""

    def test_sustained_load(self):
        """
        Test handling sustained load of 100 requests.

        Performance Target: All requests complete successfully
        """
        # Create test org
        org_id = f"org_throughput_{int(time.time())}"
        user_email = f"throughput_{int(time.time())}@test.com"

        requests.post(f"{API_BASE_URL}/organizations/", json={
            "id": org_id,
            "name": "Throughput Org"
        })

        signup_response = requests.post(f"{API_BASE_URL}/auth/signup", json={
            "email": user_email,
            "password": "Test123!",
            "name": "Throughput User",
            "org_id": org_id
        })
        token = signup_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Make 100 GET requests
        def get_people():
            response = requests.get(
                f"{API_BASE_URL}/people/?org_id={org_id}",
                headers=headers
            )
            return response.status_code

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_people) for _ in range(100)]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()

        # All requests should succeed
        success_count = sum(1 for status in results if status == 200)
        total_time = end_time - start_time
        throughput = len(results) / total_time

        print(f"\n📊 Sustained load (100 requests):")
        print(f"   Successful: {success_count}/100")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Throughput: {throughput:.2f} req/s")

        # All requests should succeed
        assert success_count == 100, f"Only {success_count}/100 requests succeeded"
