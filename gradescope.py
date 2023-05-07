# Test your huffman.py locally and quickly 
# make sure this file in in the same folder as your huffman.py

import random
from huffman import compress, decompress

# Feel free to change the size of the bytes generated
size = 1000

input_bytes = bytes([random.randint(0, 255) for _ in range(size)])

compressed_bytes, decoder_ring = compress(input_bytes)

decompressed_bytes = decompress(compressed_bytes, decoder_ring)

assert input_bytes == decompressed_bytes

# --------------------------------------------------------------------------------