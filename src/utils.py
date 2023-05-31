import math


def str2z(string):
    return int.from_bytes(string.encode('utf-8'), byteorder='big', signed=False)

def z2str(z):
    return (z).to_bytes(math.ceil((z).bit_length() / 8), byteorder = 'big', signed=False).decode('utf-8')

def strattr2zattr(string):
    '''
    string in the format of "attribute@location_id"
    `id` has to be a number in [0,2**32-1]
    '''
    attribute, identity = string.split('_')
    attr_z = str2z(attribute)

    identity_z = int(identity)
    if (identity_z).bit_length() > 32:
        raise Exception

    return attr_z * (2**32) + int(identity)

def zattr2strattr(z):
    attr_z, identity_z = divmod(z, 2**32)
    attribute = z2str(attr_z)

    return attribute + '_' + str(identity_z)


def msp2M(msp):
    theta = len(max(msp.values(), key=len))
    d = {}
    for n, (k,v) in enumerate(msp.items(), start=1):
        d[n] = {'index':k}
        local_len = len(v)
        for i in range(local_len):
            d[n][i+1] = v[i]
        for j in range(local_len, theta):
            d[n][j+1] = 0
    return d
