"""
Test Script - Load Testing
Tests the API with 10, 20, and 30 concurrent requests
"""
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Test image URLs with people
TEST_IMAGES = [
    "https://images.pexels.com/photos/1054218/pexels-photo-1054218.jpeg",  # Group of people
    "https://images.pexels.com/photos/1154638/pexels-photo-1154638.jpeg",  # People walking
    "https://images.pexels.com/photos/1587927/pexels-photo-1587927.jpeg",  # Person
    "https://images.pexels.com/photos/2102416/pexels-photo-2102416.jpeg",  # Multiple people
    "https://images.pexels.com/photos/3184296/pexels-photo-3184296.jpeg",  # Group
]

API_URL = "http://localhost:5000"


def send_request(image_url, request_id):
    """Send a single request to the API"""
    start_time = time.time()
    
    try:
        # Send request to queue the task
        response = requests.post(
            f"{API_URL}/analyze_img",
            json={'url': image_url},
            timeout=5
        )
        
        submit_time = time.time() - start_time
        
        if response.status_code == 202:
            task_id = response.json()['task_id']
            
            # Poll for result
            max_attempts = 60
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(1)
                result_response = requests.get(f"{API_URL}/result/{task_id}", timeout=5)
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    status = result['status']
                    
                    if status == 'completed':
                        total_time = time.time() - start_time
                        person_count = result.get('person_count', 0)
                        return {
                            'request_id': request_id,
                            'success': True,
                            'task_id': task_id,
                            'submit_time': submit_time,
                            'total_time': total_time,
                            'person_count': person_count
                        }
                    elif status == 'failed':
                        return {
                            'request_id': request_id,
                            'success': False,
                            'error': result.get('error', 'Unknown error')
                        }
                
                attempt += 1
            
            return {
                'request_id': request_id,
                'success': False,
                'error': 'Timeout waiting for result'
            }
        else:
            return {
                'request_id': request_id,
                'success': False,
                'error': f'Failed to submit task: {response.status_code}'
            }
    
    except Exception as e:
        return {
            'request_id': request_id,
            'success': False,
            'error': str(e)
        }


def run_load_test(num_requests, test_name):
    """Run load test with specified number of concurrent requests"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name} - {num_requests} concurrent requests")
    print(f"{'='*60}")
    
    # Prepare request data
    requests_data = []
    for i in range(num_requests):
        image_url = TEST_IMAGES[i % len(TEST_IMAGES)]
        requests_data.append((image_url, i + 1))
    
    # Send requests concurrently
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = {
            executor.submit(send_request, url, req_id): req_id 
            for url, req_id in requests_data
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✓ Request #{result['request_id']}: "
                      f"{result['person_count']} person(s) detected "
                      f"(total: {result['total_time']:.2f}s)")
            else:
                print(f"✗ Request #{result['request_id']}: {result['error']}")
    
    total_duration = time.time() - start_time
    
    # Calculate statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n{'-'*60}")
    print(f"Summary:")
    print(f"  Total requests: {num_requests}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    print(f"  Total time: {total_duration:.2f}s")
    
    if successful:
        submit_times = [r['submit_time'] for r in successful]
        total_times = [r['total_time'] for r in successful]
        
        print(f"\n  Submit time (API response):")
        print(f"    Min: {min(submit_times):.3f}s")
        print(f"    Max: {max(submit_times):.3f}s")
        print(f"    Avg: {statistics.mean(submit_times):.3f}s")
        
        print(f"\n  Total time (including processing):")
        print(f"    Min: {min(total_times):.2f}s")
        print(f"    Max: {max(total_times):.2f}s")
        print(f"    Avg: {statistics.mean(total_times):.2f}s")
        
        print(f"\n  Throughput: {num_requests / total_duration:.2f} requests/second")
    
    return results


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is healthy and running")
            return True
        else:
            print("✗ API is not healthy")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print(f"Make sure the API is running on {API_URL}")
        return False


def main():
    """Main test runner"""
    print("="*60)
    print("API Load Testing Tool")
    print("="*60)
    
    # Check API health
    if not check_api_health():
        return
    
    print("\nMake sure at least one consumer worker is running!")
    input("Press Enter to start testing...")
    
    # Run tests with increasing load
    test_configurations = [
        (10, "Light Load"),
        (20, "Medium Load"),
        (30, "Heavy Load")
    ]
    
    all_results = {}
    
    for num_requests, test_name in test_configurations:
        results = run_load_test(num_requests, test_name)
        all_results[test_name] = results
        
        # Wait between tests
        if num_requests < 30:
            print("\nWaiting 5 seconds before next test...")
            time.sleep(5)
    
    # Final summary
    print(f"\n{'='*60}")
    print("Final Summary - All Tests")
    print(f"{'='*60}")
    
    for test_name, results in all_results.items():
        successful = len([r for r in results if r['success']])
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        print(f"{test_name:20s}: {successful}/{total} successful ({success_rate:.1f}%)")


if __name__ == '__main__':
    main()
