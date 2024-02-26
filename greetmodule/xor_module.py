
def xor_bytes(input_bytes):
    # output_bytes = bytes(x ^ 0xFF for x in input_bytes)
    output_bytes = bytes(x + 1 for x in input_bytes)
    print(input_bytes)
    print(output_bytes)
    return output_bytes

