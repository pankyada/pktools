from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_neo4j_data(url, auth, body):
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(body))
    response.raise_for_status()
    return response.json()

def convert_neo4j_to_force_graph(neo4j_response):
    nodes = []
    links = []

    for result in neo4j_response['results']:
        for data in result['data']:
            for index, row_item in enumerate(data['row']):
                if row_item and row_item != {}:
                    meta = data['meta'][index]
                    print(row_item, meta['elementId'])
                    if 'title' in row_item:
                        if 'tagline' in row_item:
                            nodes.append({
                                'id': meta['elementId'],
                                'name': row_item['title'],
                                'tagline': row_item['tagline'],
                                'released': row_item['released'],
                                'color': '#FF5733',
                                'type': 'movie'
                            })
                        else:
                            nodes.append({
                                'id': meta['elementId'],
                                'name': row_item['title'],
                                'released': row_item['released'],
                                'color': '#FF5733',
                                'type': 'movie'
                            })
                    elif 'name' in row_item:
                        if 'born' in row_item:
                            nodes.append({
                                'id': meta['elementId'],
                                'name': row_item['name'],
                                'born': row_item['born'],
                                'color': '#33FF57',
                                'type': 'person'
                            })
                        else:
                            nodes.append({
                                'id': meta['elementId'],
                                'name': row_item['name'],
                                'color': '#33FF57',
                                'type': 'person'
                            })

            if len(data['meta']) > 1:
                links.append({
                    'source': data['meta'][0]['elementId'],
                    'target': data['meta'][2]['elementId']
                })

    return {'nodes': nodes, 'links': links}

@app.route('/fetch-formatted-data', methods=['POST'])
def fetch_formatted_data():
    # Replace with your Neo4J credentials
    neo4j_username = ''
    neo4j_password = ''
    url = "http://localhost:7474/db/neo4j/tx"
    auth = HTTPBasicAuth(neo4j_username, neo4j_password)

    try:
        # Extract the Cypher query from the request body
        request_data = request.get_json()
        cypher_query = request_data.get('query')

        if not cypher_query:
            return jsonify({'error': 'Cypher query is required'}), 400

        body = {
            "statements": [
                {
                    "statement": cypher_query
                }
            ]
        }

        neo4j_response = fetch_neo4j_data(url, auth, body)
        converted_response = convert_neo4j_to_force_graph(neo4j_response)
        return jsonify(converted_response)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to an available port
