from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv
import redis
from datetime import datetime
import json

load_dotenv()

class Config:
    API_KEY = os.getenv('API_NINJA_KEY')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_CACHE_DURATION = int(os.getenv('REDIS_CACHE_DURATION', 300))  # 5 minutes in seconds
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    BASE_URL = 'https://api.api-ninjas.com/v1/dictionary'


app = Flask(__name__)
config = Config()

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
)


def cache_response(word, data):
    cache_data = {
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    redis_client.setex(
        f'word:{word}',
        config.REDIS_CACHE_DURATION,
        json.dumps(cache_data)
    )


API_KEY = os.getenv('API_NINJA_KEY')

def get_word_definition_from_api(word):
    headers = {'X-Api-Key': config.API_KEY}
    response = requests.get(f'{config.BASE_URL}?word={word}', headers=headers)
    response.raise_for_status()
    return response.json()


@app.route('/dictionary/<word>')
def get_definition(word):
    try:
        cached_data = redis_client.get(f'word:{word}')
        
        if cached_data:
            cached_response = json.loads(cached_data)
            return jsonify({
                'data': cached_response['data'],
                'source': 'redis_cache',
                'cached_at': cached_response['timestamp']
            })
        
        api_response = get_word_definition_from_api(word)
        
        cache_response(word, api_response)
        
        return jsonify({
            'data': api_response,
            'source': 'api_ninjas'
        })
            
    except requests.RequestException as e:
        return jsonify({
            'error': 'API request failed',
            'message': str(e)
        }), 500
    except redis.RedisError as e:
        return jsonify({
            'error': 'Redis error',
            'message': str(e)
        }), 500


@app.route('/random_word')
def random_word():
    try:
        api_url = 'https://api.api-ninjas.com/v1/randomword'
        response = requests.get(api_url, headers={'X-Api-Key': f"{API_KEY}"})

        if response.status_code == requests.codes.ok:
            print(response.text)
        else:
            print("Error:", response.status_code, response.text)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': 'Failed to fetch definition',
                'status_code': response.status_code,
                'message': response.text
            }), response.status_code
            
    except requests.RequestException as e:
        return jsonify({
            'error': 'API request failed',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)

