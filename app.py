from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('API_NINJA_KEY')

@app.route('/dictionary/<word>')
def get_definition(word):
    try:
        api_url = 'https://api.api-ninjas.com/v1/dictionary?word={}'.format(word)
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


@app.route('/randomword')
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
    app.run(debug=True)

