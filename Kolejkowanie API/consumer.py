"""
Consumer - Worker Process
Processes images from queue and detects people using HOG detector
Can be run multiple times to scale horizontally
"""
import redis
import json
import cv2
import numpy as np
import requests
from io import BytesIO
import time
import sys

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Initialize HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def download_image(url):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        raise Exception(f"Failed to download image: {str(e)}")


def detect_people(image):
    """Detect people in image using HOG detector"""
    try:
        # Resize for faster detection
        height, width = image.shape[:2]
        max_dimension = 800
        
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # Detect people in the image
        boxes, weights = hog.detectMultiScale(
            image, 
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )
        
        return len(boxes)
    except Exception as e:
        raise Exception(f"Failed to detect people: {str(e)}")


def process_task(task_data):
    """Process a single task"""
    task_id = task_data['task_id']
    image_url = task_data['image_url']
    
    print(f"[{task_id}] Processing image: {image_url}")
    
    try:
        # Update status to processing
        redis_client.set(f'task:{task_id}:status', 'processing')
        
        # Download image
        print(f"[{task_id}] Downloading image...")
        image = download_image(image_url)
        
        if image is None:
            raise Exception("Failed to decode image")
        
        # Detect people
        print(f"[{task_id}] Detecting people...")
        person_count = detect_people(image)
        
        # Store result
        redis_client.set(f'task:{task_id}:result', person_count)
        redis_client.set(f'task:{task_id}:status', 'completed')
        
        print(f"[{task_id}] Completed! Found {person_count} person(s)")
        
    except Exception as e:
        error_message = str(e)
        print(f"[{task_id}] Error: {error_message}")
        redis_client.set(f'task:{task_id}:status', 'failed')
        redis_client.set(f'task:{task_id}:error', error_message)


def main():
    """Main consumer loop"""
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    print(f"Starting consumer worker #{worker_id}")
    print("Waiting for tasks...")
    
    while True:
        try:
            # Block and wait for task from queue (BRPOP - blocking right pop)
            result = redis_client.brpop('image_analysis_queue', timeout=1)
            
            if result:
                queue_name, task_json = result
                task_data = json.loads(task_json)
                process_task(task_data)
            
        except KeyboardInterrupt:
            print(f"\nWorker #{worker_id} shutting down...")
            break
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(1)


if __name__ == '__main__':
    main()
