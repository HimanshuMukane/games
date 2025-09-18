def decode_numbers(seq):
    result = []
    for num in seq:
        if num == 100:  # space
            result.append(" ")
        elif isinstance(num, int):  # normal number
            # A -> 0, B -> 1, etc., so letter = chr(num + 65)
            if 0 <= num <= 25:
                result.append(chr(num + ord('A')))
            else:
                result.append("?")  # unknown / out of range
        elif isinstance(num, str):  # if it's a punctuation like "." or ","
            result.append(num)
    return "".join(result)

def decode_from_string(encrypted_string):
    """Decode from a comma-separated string like '14,13,100,19,7,4'"""
    parts = encrypted_string.split(',')
    sequence = []
    for part in parts:
        part = part.strip()
        if part == '100':
            sequence.append(100)
        elif part.isdigit():
            sequence.append(int(part))
        else:
            # It's a punctuation mark
            sequence.append(part)
    return decode_numbers(sequence)


# Your sequence as a list (replacing em dash with regular dash)
sequence = [
6,14,100,19,14,100,15,11,0,2,4,18,100,14,5,100,13,4,22,100,1,14,17,13,100,22,7,4,17,4,100,24,14,20,100,11,8,21,4,3,100,14,13,2,4,100,1,17,4,0,19,7,4,3,100,2,7,4,17,8,18,7,4,3,100,18,19,14,15,100,1,24,100,19,7,4,100,18,4,2,14,13,3,100,18,4,13,19,8,13,4,11,100,18,19,0,13,3,8,13,6,100,19,0,11,11,100,19,7,4,100,6,20,0,17,3,8,0,13,100,7,8,3,4,18,100,12,0,13,24,100,13,20,12,1,4,17,18,100,1,20,19,100,14,13,11,24,100,19,7,4,100,14,13,4,100,22,17,0,15,15,4,3,100,8,13,100,2,17,8,12,18,14,13,100,17,4,21,4,0,11,18,100,19,7,4,100,22,0,24,100,5,14,17,22,0,17,3
]

# Test with the list
decoded_text = decode_numbers(sequence)
print("Decoded from list:")
print(decoded_text)
print()
