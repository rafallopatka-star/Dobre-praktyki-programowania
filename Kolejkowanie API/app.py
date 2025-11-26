"""
Flask API - Producer
Endpoint /analyze_img that receives image URL and queues analysis task
"""
from flask import Flask, request, jsonify
import redis
import uuid
import json
from datetime import datetime

app = Flask(__name__)

# Connect to Redis (message broker/queue)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/analyze_img', methods=['GET', 'POST'])
def analyze_img():
    """
    Endpoint that receives image URL and queues it for analysis
    Returns task_id for tracking the analysis
    """
    try:
        # Get image URL from request
        if request.method == 'POST':
            data = request.get_json()
            image_url = data.get('url')
        else:  # GET
            image_url = request.args.get('url')
        
        if not image_url:
            return jsonify({'error': 'Missing url parameter'}), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create task data
        task_data = {
            'task_id': task_id,
            'image_url': image_url,
            'status': 'queued',
            'created_at': datetime.now().isoformat()
        }
        
        # Push task to Redis queue
        redis_client.lpush('image_analysis_queue', json.dumps(task_data))
        
        # Store task status
        redis_client.set(f'task:{task_id}:status', 'queued')
        
        return jsonify({
            'task_id': task_id,
            'status': 'queued',
            'message': 'Task queued for processing'
        }), 202
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    """
    Check the status and result of a task
    """
    try:
        status = redis_client.get(f'task:{task_id}:status')
        
        if not status:
            return jsonify({'error': 'Task not found'}), 404
        
        result = {
            'task_id': task_id,
            'status': status
        }
        
        # If task is completed, get the person count
        if status == 'completed':
            person_count = redis_client.get(f'task:{task_id}:result')
            if person_count:
                result['person_count'] = int(person_count)
        
        # If task failed, get error message
        if status == 'failed':
            error = redis_client.get(f'task:{task_id}:error')
            if error:
                result['error'] = error
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return jsonify({'status': 'healthy', 'redis': 'connected'}), 200
    except:
        return jsonify({'status': 'unhealthy', 'redis': 'disconnected'}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
