
import json
import os
import uuid
from datetime import datetime
from urllib.parse import urlparse

import pika
from flask import Flask, jsonify, request

import task_store

app = Flask(__name__)

RABBIT_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBIT_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBIT_USER = os.getenv('RABBITMQ_USER')
RABBIT_PASS = os.getenv('RABBITMQ_PASS')
QUEUE_NAME = os.getenv('RABBITMQ_QUEUE', 'image_analysis_queue')

task_store.init_db()


@app.route('/', methods=['GET'])
def index():
    return jsonify(
        {
            'message': 'Image analysis API',
            'endpoints': {
                'queue_image': '/analyze_img',
                'get_result': '/result/<task_id>',
                'health': '/health',
            },
        }
    ), 200


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


def _publish_task(task_payload: dict) -> None:
    connection = pika.BlockingConnection(_rabbit_parameters())
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(task_payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


@app.route('/analyze_img', methods=['GET', 'POST'])
def analyze_img():
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            image_url = data.get('url')
        else:
            image_url = request.args.get('url')

        if not image_url:
            return jsonify({'error': 'Missing url parameter'}), 400

        if not _is_valid_url(image_url):
            return jsonify({'error': 'Invalid url parameter'}), 400

        task_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        task_store.upsert_task(
            task_id=task_id,
            url=image_url,
            status='queued',
        )

        payload = {
            'task_id': task_id,
            'image_url': image_url,
            'created_at': created_at,
        }

        _publish_task(payload)

        return (
            jsonify(
                {
                    'task_id': task_id,
                    'status': 'queued',
                    'message': 'Task queued for processing',
                }
            ),
            202,
        )

    except Exception as exc:  # pragma: no cover - defensive
        return jsonify({'error': str(exc)}), 500


@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id: str):
    task = task_store.get_task(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    response = {
        'task_id': task['task_id'],
        'status': task['status'],
        'url': task['url'],
        'created_at': task['created_at'],
        'updated_at': task['updated_at'],
    }

    if task['status'] == 'completed':
        response['person_count'] = task.get('person_count', 0) or 0
        if task.get('output_path'):
            response['output_path'] = task['output_path']

    if task['status'] == 'failed' and task.get('error'):
        response['error'] = task['error']

    return jsonify(response), 200


@app.route('/health', methods=['GET'])
def health():
    try:
        connection = pika.BlockingConnection(_rabbit_parameters())
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        connection.close()

        task_store.init_db()
        return jsonify({'status': 'healthy', 'rabbitmq': 'connected'}), 200
    except Exception as exc:
        return jsonify({'status': 'unhealthy', 'rabbitmq': 'disconnected', 'error': str(exc)}), 503


if __name__ == '__main__':
    task_store.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
