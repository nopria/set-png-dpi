# set-png-dpi
This software sets or changes the DPI metadata information of a PNG image file. It is based on specifications of PNG image format given at https://www.w3.org/TR/PNG/

Features:
- file name is not checked for PNG extension;
- no reencoding if image nor validation of PNG format for faster processing;
- although complete PNG format validation is NOT performed, file is checked for PNG initial signature and for individual PNG chunk CRC32 validation. Therefore, malformed or corrupted PNG images may or may not generate an error;
- PNG image file is modified “in place”. Metadata are overwritten if already present (file length does not change) or added if not present (file length increases by exactly 21 bytes);
- no backup copy of original file is made unless you uncomment a specified line.

Enjoy!
