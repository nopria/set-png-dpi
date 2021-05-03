# set-png-dpi
This code sets or changes the DPI metadata information of a PNG image file. It is based on specifications of PNG image format given at https://www.w3.org/TR/PNG/

Features:
- file name is (intentionally) not checked for PNG extension;
- no re-encoding of image nor validation of PNG format;
- although complete PNG format validation is **not** performed, file is checked for PNG initial signature and for individual PNG chunk CRC validation. Therefore, malformed or corrupted PNG images may or may not generate an error;
- PNG image file is modified “in place”. Density metadata are **overwritten** if already present (file length does not change) or **added** if not present (file length increases by exactly 21 bytes);
- no backup copy of original file is made unless you uncomment a specified line (see code comments).

Usage examples:

````
python set-png-dpi <filename> <horizontal DPI> <vertical DPI> [quiet]

python set-png-dpi image.png 150 150
python set-png-dpi image.png 300 300 quiet
python set-png-dpi image.png 150 300
````

Enjoy!
