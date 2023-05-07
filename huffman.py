import marshal
import os
import pickle
import sys
from array import array
from typing import Dict
from typing import Tuple
import heapq
from collections import Counter

#### Correctness -------------------------------------------------------------------------------------------------
## for every input byte, there is a unique huffman code corresponding to a leaf node on a binary tree, where the path from the root to the leaf node determines the code for that symbol.
# for each parent node the left child has the higher frequency and the right the lower as huffman merges the two least frequent symbols in each iteration, 
## for every input byte, no code assigned to a byte is a prefix of any other code assigned to another byte. 
# The most frequent byte has a shorter code
##### Termination ------------------------------------------------------------------------------------------------

def compress(message: bytes) -> Tuple[bytes, Dict]:
    """ Given the bytes read from a file, calls encode and turns the string into an array of bytes to be written to disk.

    :param message: raw sequence of bytes from a file
    :returns: bytes to be written to disk
              dict containing the decoder ring
    """
    encoded_msg, decoder_ring = encode(message)

    pad = 0
    if len(encoded_msg) % 8 != 0:
        pad = 8 - len(encoded_msg) % 8
        encoded_msg += '0' * pad

    pad2 = encoded_msg.find('1')

    compressed_msg = bytes([int(encoded_msg[bit: bit + 8], 2) for bit in range(0, len(encoded_msg), 8)])

    return bytes([pad, pad2]) + compressed_msg, decoder_ring


def decompress(message: array, decoder_ring: Dict) -> bytes:
    """ Given a decoder ring and an array of bytes read from a compressed file, turns the array into a string and calls decode.

    :param message: array of bytes read in from a compressed file
    :param decoder_ring: dict containing the decoder ring
    :return: raw sequence of bytes that represent a decompressed file
    """

    pad = message[0] 
    pad2 =  message[1]

    encoded_msg = bin(int.from_bytes(message[2:], byteorder='big'))[2:]
    if pad != 0:
        encoded_msg = encoded_msg[:-pad]

    encoded_msg = '0' * pad2 + encoded_msg

    return decode(encoded_msg, decoder_ring)


class Node:
    def __init__(self, byte, frequency):
        self.byte = byte
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


def make_huffman_tree(frequencies: dict):
    """ Given a frequency makes a binary search tree
    :param frequency: byte and their frequency in a dictionary
    :returns: a node
    """
    nodes = [Node(byte, freq) for byte, freq in frequencies.items()]

    heapq.heapify(nodes)

    while len(nodes) > 1:
        left_child = heapq.heappop(nodes)
        right_child = heapq.heappop(nodes)

        parent = Node(byte = None, frequency= left_child.frequency + right_child.frequency)
        parent.left = left_child
        parent.right = right_child

        heapq.heappush(nodes, parent)

    return nodes[0]


def traverse_tree(node: Node, code: str, code_table: Dict):
    """
    Traverse tree and return the encoding table
    """
    if node is None:
        return
    if  node.byte is not None:
        code_table[node.byte] = code
    
    traverse_tree(node.left, code + '0', code_table)
    traverse_tree(node.right, code + '1', code_table)

    return code_table


def encode(message: bytes) -> Tuple[str, Dict]:
    """ Given the bytes read from a file, encodes the contents using the Huffman encoding algorithm.

    :param message: raw sequence of bytes from a file
    :returns: string of 1s and 0s representing the encoded message
              dict containing the decoder ring as explained in lecture and handout.
    """

    freq = Counter(message)
    tree = make_huffman_tree(freq)
    code_table = traverse_tree(tree, "", {})

    encoded_msg = ''.join([code_table[byte] for byte in message])
    
    return [encoded_msg, code_table]


def decode(message: str, decoder_ring: Dict) -> bytes:
    """ Given the encoded string and the decoder ring, decodes the message using the Huffman decoding algorithm.

    :param message: string of 1s and 0s representing the encoded message
    :param decoder_ring: dict containing the decoder ring
    return: raw sequence of bytes that represent a decoded file
    """
    code_to_byte = { value: key for key, value in decoder_ring.items() }
    original_message = []
    code = ""
    
    for char in message:
        code += char
        if code in code_to_byte.keys():
            original_message.append(code_to_byte[code])
            code = ""

    return bytes(original_message)


if __name__ == '__main__':
    usage = f'Usage: {sys.argv[0]} [ -c | -d | -v | -w ] infile outfile'
    if len(sys.argv) != 4:
        raise Exception(usage)

    operation = sys.argv[1]
    if operation not in {'-c', '-d', '-v', 'w'}:
        raise Exception(usage)

    infile, outfile = sys.argv[2], sys.argv[3]
    if not os.path.exists(infile):
        raise FileExistsError(f'{infile} does not exist.')

    if operation in {'-c', '-v'}:
        with open(infile, 'rb') as fp:
            _message = fp.read()

        if operation == '-c':
            _message, _decoder_ring = compress(_message)
            with open(outfile, 'wb') as fp:
                marshal.dump((pickle.dumps(_decoder_ring), _message), fp)
        else:
            _message, _decoder_ring = encode(_message)
            print(_message)
            with open(outfile, 'wb') as fp:
                marshal.dump((pickle.dumps(_decoder_ring), _message), fp)

    else:
        with open(infile, 'rb') as fp:
            pickleRick, _message = marshal.load(fp)
            _decoder_ring = pickle.loads(pickleRick)

        if operation == '-d':
            bytes_message = decompress(array('B', _message), _decoder_ring)
        else:
            bytes_message = decode(_message, _decoder_ring)
        with open(outfile, 'wb') as fp:
            fp.write(bytes_message)
