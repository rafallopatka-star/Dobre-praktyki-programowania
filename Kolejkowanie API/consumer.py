
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import cv2
import numpy as np
import pika
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import task_store

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

RABBIT_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBIT_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBIT_USER = os.getenv('RABBITMQ_USER')
RABBIT_PASS = os.getenv('RABBITMQ_PASS')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'image_analysis_queue')
OUTPUT_DIR = Path(__file__).parent / 'analyzed_images'

_retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=frozenset(['GET']))
_adapter = HTTPAdapter(max_retries=_retry)
_session = requests.Session()
_session.mount('http://', _adapter)
_session.mount('https://', _adapter)


def _rabbit_parameters() -> pika.ConnectionParameters:
    credentials = None
    if RABBIT_USER and RABBIT_PASS:
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)

    return pika.ConnectionParameters(
        host=RABBIT_HOST,
        port=RABBIT_PORT,
        credentials=credentials,
        heartbeat=30,
    )


def download_image(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (image-fetcher)"}
        response = _session.get(url, timeout=10, headers=headers, allow_redirects=True)
        response.raise_for_status()
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except Exception as exc:
        raise Exception(f'Failed to download image: {exc}')


def detect_people(image) -> int:
    try:
        height, width = image.shape[:2]
        max_dimension = 800

        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            image = cv2.resize(image, (int(width * scale), int(height * scale)))

        boxes, _ = hog.detectMultiScale(
            image,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
        )

        return len(boxes)
    except Exception as exc:
        raise Exception(f'Failed to detect people: {exc}')


def save_image(image, task_id: str, person_count: int, image_url: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(image_url)
    ext = Path(parsed.path).suffix or '.jpg'
    filename = f"{task_id}-{person_count}{ext}"
    output_path = OUTPUT_DIR / filename
    cv2.imwrite(str(output_path), image)
    return str(output_path)


def process_task(task_data: dict):
    task_id = task_data['task_id']
    image_url = task_data['image_url']

    print(f"[{task_id}] Processing image: {image_url}")
    task_store.mark_status(task_id, 'processing')

    try:
        image = download_image(image_url)
        if image is None:
            raise Exception('Failed to decode image')

        person_count = detect_people(image)
        saved_path = save_image(image, task_id, person_count, image_url)

        task_store.mark_status(
            task_id,
            status='completed',
            person_count=person_count,
            output_path=saved_path,
        )

        print(f"[{task_id}] Completed! Found {person_count} person(s)")

    except Exception as exc:
        error_message = str(exc)
        task_store.mark_status(task_id, status='failed', error=error_message)
        print(f"[{task_id}] Error: {error_message}")
        raise


def on_message(channel, method, properties, body):
    try:
        task_data = json.loads(body)
        process_task(task_data)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    worker_id = sys.argv[1] if len(sys.argv) > 1 else '1'
    print(f"Starting consumer worker #{worker_id}")
    task_store.init_db()

    try:
        connection = pika.BlockingConnection(_rabbit_parameters())
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message, auto_ack=False)

        print('Waiting for tasks...')
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\nWorker #{worker_id} shutting down...")
    except Exception as exc:
        print(f"Worker #{worker_id} encountered an error: {exc}")
        time.sleep(1)


if __name__ == '__main__':
    main()
