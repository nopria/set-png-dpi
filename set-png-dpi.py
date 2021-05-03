# specifications of PNG image format at https://www.w3.org/TR/PNG/

# PNG initial signature - 8 bytes
# 89504E470D0A1A0A (137 80 78 71 13 10 26 10)

# PNG chunk structure
# data length: 4 bytes (values from 0 to 256^4)
# type: 4 bytes (numeric values: 65 to 90 and 97 to 122, corresponding to ASCII uppercase and lowercase letters)
# data: a sequence of bytes having length defined above (absent if data length = 0)
# CRC: 4 bytes (CRC32 on type+data)

# after initial signature, IHDR chunk (total lenght 25 bytes) must be the first

# DPI density information of a PNG image is recorded in pHYs chunk
# 00000009 (9 bytes data)
# 70485973 ('pHYs', 112 72 89 115)
# data: x_density / 4 bytes + y_resolution / 4 bytes + unit / 1 byte (0=unknown, 1=meter)
# CRC 4 bytes

import sys,os,zlib,shutil

# 1st command line argument: PNG file to process
filename = sys.argv[1]

# 2nd and 3rd command line arguments: horizontal and vertical DPI
x_density = int(sys.argv[2]) # in Dots Per Inch
y_density = int(sys.argv[3]) # in Dots Per Inch

x_density_m = round(x_density * 100 / 2.54) # calculate density in dots per meter, as requested by PNG format specifications
y_density_m = round(y_density * 100 / 2.54)

assert x_density_m > 0 and x_density_m < 4294967296 # = 256^4 = 4 bytes unsigned integer
assert y_density_m > 0 and y_density_m < 4294967296

pHYs_len  = bytes([0,0,0,9]) # same as int(9).to_bytes(4,'big')
pHYs_type = b'pHYs'
pHYs_data = x_density_m.to_bytes(4,'big') + y_density_m.to_bytes(4,'big')+bytes([1])
pHYs_crc = zlib.crc32(pHYs_type+pHYs_data).to_bytes(4,'big')

# 4th (optional) command line argument: quiet processing
echo = True
if len(sys.argv) > 4:
    if sys.argv[4] == 'quiet':
        echo = False


def read_png_chunk(f):
    """
    Yields all chunks of a PNG image file, performing individual chunk CRC validation.
    Make sure to have read the initial PNG signature.
    :yield: a tuple of byte strings defining a complete chunk: (length, type, data, CRC).
    """
    while True:
        chunk_len = f.read(4)
        if len(chunk_len) != 4: # if less than 4 bytes were read, file has ended or PNG is corrupted; in any case chunks reading stops
            return None
        chunk_typ = f.read(4)
        chunk_dat = f.read(int.from_bytes(chunk_len, byteorder='big'))
        chunk_crc = f.read(4)
        computed_crc = zlib.crc32(chunk_typ+chunk_dat).to_bytes(4,'big')
        if not chunk_crc == computed_crc:
            raise Exception("File '"+os.path.split(filename)[1]+"' is a malformed or corrupted PNG image: CRC validation of PNG chunk '" + chunk_typ.decode() +"' failed.")
        yield chunk_len, chunk_typ, chunk_dat, chunk_crc


pHYs_exist = False # flag needed to separate2 cases: (1) pHYs chunk exists and must be overwritten, (2) pHYs chunk exists and must be added
with open(filename, 'rb+') as f:
    initial_signature = f.read(8)
    if initial_signature == bytes.fromhex('89504E470D0A1A0A'): # processed file has a valid PNG initial signature
        # shutil.copy(filename, filename+'.original') # uncomment this line to make a backup copy of the file before it is modified in place
        pass
    else: # processed file is not a valid PNG image
        raise Exception("File '"+os.path.split(filename)[1]+"' is not a valid PNG image: initial PNG signature is missing.")
    for chunk_len, chunk_typ, chunk_dat, chunk_crc in read_png_chunk(f):
        if chunk_len == pHYs_len and chunk_typ == pHYs_type: # pHYs chunk exist in PNG file
            pHYs_exist = True
            f.seek(f.tell()-4-9) # go back to start of pHYs data (relative seek does not work with files opened with 'rb+')
            if echo: print("Setting density of '" + os.path.split(filename)[1] + "' to " + str(x_density) + "x" + str(y_density) + " DPI.")
            f.write(pHYs_data+pHYs_crc) # overwriting existing pHYs chunk
            if echo: print("Done.")
            break # pHYs chunk has been updated in place, no need to read subsequent PNG chunks, program can end
    if not pHYs_exist: # pHYs chunk was not found, it will be inserted in PNG file as 2nd chunk after IHDR, which ends at 33rd byte
        f.seek(33) # go back to start of 2nd chunk
        remaining_chunks = f.read() # read all chunks after 1st one (IHDR)
        f.seek(33) # go back to start of 2nd chunk
        f.write(pHYs_len+pHYs_type+pHYs_data+pHYs_crc) # write pHYs chunk
        f.write(remaining_chunks) # write all original chunks after 1st one
