from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', defaults={'path':''})
@app.route('/<path:path>')
def main(path):
  proto = request.environ.get('SERVER_PROTOCOL')
  print('--')
  print(f'Received request from {request.remote_addr}')
  print(f'{request.method} {path} {proto}')
  [print(f'{k}: {v}') for (k,v) in request.headers.items()] 
  [print(f'Param: {k}: {v}') for (k,v) in request.args.items()] 
  return "<p>OK</p>"

@app.route('/healthcheck')
def healthcheck():
  print('** HEALTHCHECK **')
  return '', 204

if __name__ == '__main__':
  app.run(debug=True, port=5001)
