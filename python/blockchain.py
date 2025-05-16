import hashlib
import json
from time import time
from flask import Flask, jsonify, request
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()  # Conjunto de nodos en la red
        self.new_block(previous_hash='1', proof=100)  # Crear el bloque génesis

    def new_block(self, proof, previous_hash=None):
        """Crear un nuevo bloque y añadirlo a la cadena"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []  # Reiniciar las transacciones actuales
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """Añadir una nueva transacción a la lista de transacciones"""
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1  # Retorna el índice del bloque al que se añadirá la transacción

    def register_node(self, address):
        """Añadir un nuevo nodo a la lista de nodos"""
        if address not in self.nodes:
            self.nodes.add(address)

    def resolve_conflicts(self):
        """Algoritmo de consenso para resolver conflictos"""
        new_chain = None
        max_length = len(self.chain)

        # Buscar la cadena más larga entre los nodos
        for node in self.nodes:
            print(f"Consultando nodo: {node}")  # Imprimir para depuración
            response = requests.get(f'http://{node}/chain')
            print(response.status_code, response.json())  # Imprimir código de estado y contenido de la respuesta

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Solo reemplazar si la cadena es más larga y válida
                if length > max_length and self.is_valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True  # Se reemplazó la cadena

        return False  # No se realizó el reemplazo

    @staticmethod
    def is_valid_chain(chain):
        """Verifica la validez de la cadena de bloques"""
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Comprobar el hash del bloque anterior
            if block['previous_hash'] != Blockchain.hash(last_block):
                return False
            # Comprobar la validez del proof
            if not Blockchain.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1

        return True

    @staticmethod
    def hash(block):
        """Crea un hash SHA-256 de un bloque"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """Retorna el último bloque de la cadena"""
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """Algoritmo simple de Prueba de Trabajo"""
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """Verifica si la prueba es válida (comienza con 4 ceros)"""
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Crear una instancia de la clase Blockchain
blockchain = Blockchain()

app = Flask(__name__)

@app.route('/mine', methods=['GET'])
def mine():
    """Ejecuta el algoritmo de prueba de trabajo para obtener el siguiente bloque"""
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Recompensa al minero con 1 nueva transacción
    blockchain.new_transaction(
        sender="0",  # Significa que esta transacción es generada por el nodo
        recipient="your_address",
        amount=1,
    )

    # Añade el nuevo bloque a la cadena
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Crea una nueva transacción y la añade a la lista"""
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """Devuelve la cadena completa de bloques"""
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """Registra nuevos nodos en la red"""
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "No nodes provided", 400

    for node in nodes:
        blockchain.register_node(node)

    return jsonify({"message": "Nodes added", "total_nodes": list(blockchain.nodes)}), 201

@app.route('/nodes', methods=['GET'])
def get_nodes():
    """Devuelve la lista de nodos registrados"""
    return jsonify(list(blockchain.nodes)), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    try:
        replaced = blockchain.resolve_conflicts()
        if replaced:
            response = {
                'message': 'Our chain was replaced',
                'new_chain': blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': blockchain.chain
            }
        return jsonify(response), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"message": "Request error occurred", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
