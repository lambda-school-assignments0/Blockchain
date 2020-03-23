# Paste your version of blockchain.py from the basic_block_gp
# folder here

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def new_transaction(self, sender, receiver, amount):

        new_transaction = {
            'timestamp': time(),
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        }

        self.current_transactions.append(new_transaction)

        # return index of block that will hold this transaction
        future_index = self.last_block['index'] + 1
        return future_index

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # TODO: Create the block_string
        block_string = json.dumps(block, sort_keys=True)
        string_in_bytes = block_string.encode()
        # TODO: Hash this string using sha256
        hash_object = hashlib.sha256(string_in_bytes)
        hash_string = hash_object.hexdigest()

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # TODO: Return the hashed block string in hexadecimal format
        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # TODO
        guess = f'{block_string}{proof}'.encode()

        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == '000000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/', methods=['GET'])
def get():
    response = jsonify({'message': 'GET "/" status: 200'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()

    # check for proof and id
    required_params = ['proof', 'id']
    if not all(param in data for param in required_params):
        response = {'message': "Missing required params!"}
        return jsonify(response), 400

    block_string = json.dumps(blockchain.last_block, sort_keys=True)

    is_valid_proof = blockchain.valid_proof(block_string, data['proof'])

    if is_valid_proof:
        previous_hash = blockchain.hash(blockchain.last_block)
        new_block = blockchain.new_block(data['proof'], previous_hash)

        blockchain.new_transaction(sender='0', receiver=data['id'], amount=1)

        response = {
            'message': 'Congratulations!',
        }
    else:
        response = {'message': 'Invalid proof!'}

    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'last_block': blockchain.last_block,
    }

    return response


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain': blockchain.chain,
        'chain_length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions/id/<user_id>', methods=['GET'])
def get_transaction(user_id):
    id_transactions = []
    id_balance = 0

    for block in blockchain.chain:
        print(block)
        for transaction in block['transactions']:
            if transaction['sender'] == user_id or transaction['receiver'] == user_id:
                id_transactions.append(transaction)
            if transaction['sender'] == user_id:
                id_balance -= transaction.amount
            elif transaction['receiver'] == user_id:
                id_balance += transaction.amount

    if len(id_transactions) == 0:
        id_transactions.append(
            {'message': 'Error: no transactions for this user_id found!'})

    response = {
        'current_balance': id_balance,
        'transactions': id_transactions,
    }

    response = jsonify(response)

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()

    required_params = ['sender', 'reciever', 'amount']
    if not all(param in data for param in required_params):
        response = {'message': "Missing required params!"}
        return jsonify(response), 400

    index = blockchain.new_transaction(sender=data['sender'],
                                       receiver=data['receiver'],
                                       amount=data['amount'])

    response = {'message': f'Your transaction is located in block {index}'}

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000)
