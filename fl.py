# save this as app.py

from flask import Flask, request, jsonify

app = Flask(__name__)

# simple in-memory storage
stored_data = []

@app.route('/receive_data', methods=['GET', 'POST'])
def receive_data():
    global stored_data

    if request.method == 'POST':
        # Expecting JSON body: {"matrix": [[...], [...], [...]]}
        data = request.get_json()

        if not data or 'matrix' not in data:
            return jsonify({"error": "No matrix provided"}), 400

        matrix = data['matrix']
        stored_data.append(matrix)

        return jsonify({"message": "Matrix received", "matrix": matrix}), 200

    else:  # GET request
        return jsonify({"stored_data": stored_data}), 200

if __name__ == '__main__':
    # run on all interfaces so ESP32 can see it
    app.run(host='0.0.0.0', port=8000, debug=True)
