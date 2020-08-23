import io

from typing import Union


def encode(data: Union[str, bytes, int, dict, list], encoding: str = 'utf-8') -> bytes:
    if isinstance(data, int):
        return b'i' + str(data).encode() + b'e'
    elif isinstance(data, str):
        data_bytes = data.encode(encoding)
        return str(len(data_bytes)).encode() + b':' + data_bytes
    elif isinstance(data, bytes):
        return str(len(data)).encode() + b':' + data
    elif isinstance(data, list):
        return b'l' + b''.join(encode(i) for i in data) + b'e'
    elif isinstance(data, dict):
        return b'd' + b''.join(encode(key) + encode(value) for key, value in data.items()) + b'e'
    else:
        raise TypeError('only str, bytes, int, dict and list are allowed')


def decode(bencoded_data: Union[bytes, io.BytesIO]) -> Union[bytes, int, dict, list, None]:
    if isinstance(bencoded_data, bytes):
        buffer = io.BytesIO(bencoded_data)
    else:
        buffer = bencoded_data

    test_byte = buffer.read(1)
    if test_byte == b'i':
        return int(_read_until(buffer).decode())
    elif test_byte.isdigit():
        bytes_length = test_byte + _read_until(buffer, b':')
        return buffer.read(int(bytes_length.decode()))
    elif test_byte == b'l':
        decoded_element = decode(buffer)
        decoded_list = list()
        while decoded_element is not None:
            decoded_list.append(decoded_element)
            decoded_element = decode(buffer)
        return decoded_list
    elif test_byte == b'd':
        decoded_key = decode(buffer)
        decoded_dict = dict()
        while decoded_key is not None:
            decoded_value = decode(buffer)
            decoded_dict[decoded_key] = decoded_value
            decoded_key = decode(buffer)
        return decoded_dict
    elif test_byte == b'e':
        return None
    else:
        raise OSError('not valid bencoded data')


def _read_until(buffer: io.BytesIO, stop_mark: bytes = b'e') -> bytes:
    read_buffer = b''
    i = buffer.read(1)
    while i != stop_mark:
        read_buffer += i
        i = buffer.read(1)

    return read_buffer
