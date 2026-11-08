################################################################################
# dasm: ImageParser.py
################################################################################

from typing import List
import os
import struct

from MyLog import LogLvl, MyLog

"""
Note: This file's interpretation of images is based on doc PR2000.
"""

################################################################################

# Image Sizing Params.
__MIN_IMG_SIZE  = 4     # minimum size of image (in bytes- 2 empty sections)
__MAX_IMG_SIZE  = 65536 # max size of image (in bytes- 64 KB)
__IMG_WORD_SIZE = 2     # image should only be composed of 2-byte words

# Byte/Integer Conversion Params.
__ENDIANNESS = 'big'                                    # big endian
__IS_SIGNED  = False                                    # unsigned
__FMT_END    = '<' if __ENDIANNESS == 'little' else '>'
__FMT_SIGN   = 'h' if __IS_SIGNED else 'H'              # word length

################################################################################
# Class to hold raw parsing of the image.
class RawImage():
    # Values.
    text: List[int] # 16-bit values making up the text section
    data: List[int] # 16-bit values making up the data section

    # Funcs.
    def __init__(self):
        self.text = []
        self.data = []

################################################################################
# Parse file as/into RawImage. Returns true on success. Logs own errors.
def parseAsImage(fname: str) -> tuple[bool, RawImage]:
    # Result.
    res = RawImage()

    # Image must exist.
    MyLog.log(LogLvl.INFO, f"Reading '{fname}'")
    if os.path.exists(fname) is False:
        MyLog.log(LogLvl.ERROR, f"Unable to find '{fname}'")
        return False, res

    # Check sizing.
    MyLog.log(LogLvl.DEBUG, "Running file size checks")
    imgSize = os.path.getsize(fname)
    if imgSize < __MIN_IMG_SIZE:
        MyLog.log(LogLvl.ERROR, f"File ({imgSize} bytes) is too small to be an image (min = {__MIN_IMG_SIZE} bytes))")
        return False, res
    elif imgSize > __MAX_IMG_SIZE:
        MyLog.log(LogLvl.ERROR, f"File ({imgSize} bytes) is too large to be an image (max = {__MAX_IMG_SIZE} bytes))")
        return False, res
    elif (imgSize % __IMG_WORD_SIZE) != 0:
        MyLog.log(LogLvl.ERROR, f"File ({imgSize} bytes) is not an image word multiple (word = {__IMG_WORD_SIZE} bytes))")
        return False, res

    # Open/Parse file.
    MyLog.log(LogLvl.DEBUG, f"Opening '{fname}' file/data")
    with open(fname, 'rb') as f:
        # Extract text section header.
        MyLog.log(LogLvl.DEBUG, f"Extracting text header")
        textSize = f.read(__IMG_WORD_SIZE)
        if not textSize:
            MyLog.log(LogLvl.ERROR, f"Failed to read text section header")
            return False, res
        textSize = __IMG_WORD_SIZE * int.from_bytes(textSize, byteorder=__ENDIANNESS, signed=__IS_SIGNED)
        MyLog.log(LogLvl.DEBUG, f"Text header: {textSize} bytes of text values")

        # Extract text section values.
        if textSize > 0:
            MyLog.log(LogLvl.DEBUG, f"Extracting text values")
            textVals = f.read(textSize)
            if not textVals:
                MyLog.log(LogLvl.ERROR, f"Failed to read text section values")
                return False, res
            res.text = list(struct.unpack(__FMT_END + (__FMT_SIGN * (len(textVals) // __IMG_WORD_SIZE)), textVals))
            MyLog.log(LogLvl.DEBUG, f"Text values: {len(res.text * 2)} bytes of text values")

        # Extract data section header.
        MyLog.log(LogLvl.DEBUG, f"Extracting data header")
        dataSize = f.read(__IMG_WORD_SIZE)
        if not dataSize:
            MyLog.log(LogLvl.ERROR, f"Failed to read data section header")
            return False, res
        dataSize = __IMG_WORD_SIZE * int.from_bytes(dataSize, byteorder=__ENDIANNESS, signed=__IS_SIGNED)
        MyLog.log(LogLvl.DEBUG, f"Data header: {dataSize} bytes of data values")

        # Extract data section values.
        if dataSize > 0:
            MyLog.log(LogLvl.DEBUG, f"Extracting data values")
            dataVals = f.read(dataSize)
            if not dataVals:
                MyLog.log(LogLvl.ERROR, f"Failed to read data section values")
                return False, res
            res.data = list(struct.unpack(__FMT_END + (__FMT_SIGN * (len(dataVals) // __IMG_WORD_SIZE)), dataVals))
            MyLog.log(LogLvl.DEBUG, f"Data values: {len(res.data * 2)} bytes of data values")

    # Semantic check file sizing.
    realTextSize = len(res.text) * __IMG_WORD_SIZE
    realDataSize = len(res.data) * __IMG_WORD_SIZE
    realImgSize  = (2 * __IMG_WORD_SIZE) + realTextSize + realDataSize # 2 headers + section values
    MyLog.log(LogLvl.DEBUG, f"Real image: {realImgSize} bytes ({realTextSize} text bytes, {realDataSize} data bytes)")
    if realTextSize != textSize:
        MyLog.log(LogLvl.ERROR, f"Reported text size ({(2 * __IMG_WORD_SIZE)} headers, {textSize} bytes) is incorrect ({realTextSize} bytes)")
        return False, res
    if realDataSize != dataSize:
        MyLog.log(LogLvl.ERROR, f"Reported data size ({dataSize} bytes) is incorrect ({realDataSize} bytes)")
        return False, res
    elif imgSize != realImgSize:
        MyLog.log(LogLvl.ERROR, f"Reported image size ({imgSize} bytes) is incorrect ({realImgSize} bytes)")
        return False, res

    # Heads up on empty sections (info instead of warn- PR2000 allows for such).
    if len(res.text) == 0: MyLog.log(LogLvl.INFO, "NOTE: empty text section")
    if len(res.data) == 0: MyLog.log(LogLvl.INFO, "NOTE: empty data section")
    
    # Still here? Image parsed successfully.
    return True, res
