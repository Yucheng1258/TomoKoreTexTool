try:
    from PIL import Image, ImageCms, ImageOps
    from pyswizzle import nsw_deswizzle, nsw_swizzle
    from pathlib import Path
    import io
except ImportError as e:
    print(f"An import error occurred: {e}")


def gammaedit(img:Image, gamma = 0.4545):
    return img.point(lambda x: ((x / 255) ** gamma) * 255)

def canvas_2_png(img):
    swizzle_mode = 4
    convertSize = (256,256)
    gob_w, gob_h = 1, 1
    bytes_per_block = 4
    swizzled = nsw_deswizzle(rawdata,(convertSize[0], convertSize[1]),(gob_w, gob_h),bytes_per_block,swizzle_mode)
    if select == 1 or 3:
        img = Image.frombytes('RGBA',convertSize, swizzled, 'raw', 'RGBA')
    img = img.convert()
    img = gammaedit(img)
    #img.show()
    savepath = imagePath.with_name(imagePath.stem + "CanvasOUTPUT.png")
    img.save(savepath,'png')
    print(f'Image file saved to {savepath}')
    return

def png_2_canvas(imagePath, useSrgb = False):
    imageRes = 0
    img = Image.open(imagePath)
    if img.size != (256,256):
        while True:
            try:
                print('''
                    Image is at an incorrect resolution (should be 256x256).
                    Please select an option.
                    --------------------------
                    1. Stretch and Resize
                    2. Keep aspect ratio and resize
                    3. Cancel
                    ''')
                imageRes = int(input('Select an option: '))
                if 0 < imageRes < 4:
                    break
                else:
                    print('Invalid input. Please provide a number from 1 to 3.')
            except ValueError:
                print('woah man can you input a number please?')
    if imageRes != 3:
        if imageRes == 1:
            img = img.resize((256,256),1)
        elif imageRes == 2:
            img = ImageOps.fit(img,(256,256))

        if not useSrgb:
            img = gammaedit(img,2.2)
        img = img.convert('RGBA')
        convertImg = img.tobytes('raw')
        savepath = imagePath.with_name(imagePath.stem + "OUTPUT.canvas")
        gob_w, gob_h = 1, 1
        bytes_per_block = 4
        swizzle_mode = 4
        height, width = 256,256
        linear = nsw_swizzle(convertImg,(width, height),(gob_w, gob_h),bytes_per_block,swizzle_mode)
        with open(savepath, 'wb') as f:
            f.write(bytes(linear))
        print(f'Canvas file saved to {savepath}. Please note that images with varying transparency may become opaque.')

def ugctex_2_png(img):
    convertSize = (512,512)
    gob_w, gob_h = 4, 4
    bytes_per_block = 8
    swizzle_mode = 4
    with open(Path('DDSHeader.ugctex'), 'rb') as file:
        ddsheader = file.read()
    swizzled = nsw_deswizzle(rawdata,convertSize,(gob_w, gob_h),bytes_per_block,swizzle_mode)
    img = Image.open(io.BytesIO(ddsheader+swizzled))
    img = img.convert()
    img = gammaedit(img)
    #img.show()
    savepath = imagePath.with_name(imagePath.stem + "UgcTexOUTPUT.png")
    img.save(savepath,'png')
    print(f'Image file saved to {savepath}')

def png_2_ugctex(imagePath, useSrgb = False):
    imageRes = 0
    img = Image.open(imagePath)
    convertSize = (512,512)
    if img.size != convertSize:
        while True:
            try:
                print('''
                    Image is at an incorrect resolution (should be 512x512).
                    Please select an option.
                    --------------------------
                    1. Stretch and Resize
                    2. Keep aspect ratio and resize
                    3. Cancel
                    ''')
                imageRes = int(input('Select an option: '))
                if 0 < imageRes < 4:
                    break
                else:
                    print('Invalid input. Please provide a number from 1 to 3.')
            except ValueError:
                print('woah man can you input a number please?')
    if imageRes != 3:
        if imageRes == 1:
            img = img.resize(convertSize,1)
        elif imageRes == 2:
            img = ImageOps.fit(img,convertSize)
        if not useSrgb:
            img = gammaedit(img,2.2)
    dds_bytes = io.BytesIO()
    img.save(dds_bytes,format='DDS',pixel_format='DXT1')

    savepath = imagePath.with_name(imagePath.stem + "OUTPUT.ugctex")
    gob_w, gob_h = 4, 4
    bytes_per_block = 8
    swizzle_mode = 4
    bSlice = dds_bytes.getvalue()[128:]
    swizzled = nsw_swizzle(bSlice,convertSize,(gob_w, gob_h),bytes_per_block,swizzle_mode)
    with open(savepath, 'wb') as f:
        f.write(bytes(swizzled))
    print(f'UgcTex file saved to {savepath}. Please note that images with varying transparency may become opaque.')


print('''

    Tomodachi Life: Living the Dream
    Facepaint Tool
    By Timimimi
    Thanks to RealDarkCraft for helping me with the format
    I kinda just made this script to help some friends with this
    Uses Aclios' pyswizzle library and Pillow, the friendly PIL fork (python-pillow.org).
''')
while True:
    print('''
    -------
    Functions
    -------
    1. Canvas/UgcTex to PNG
    2. PNG to Canvas/UgcTex
    3. Batch Convert Canvas/UgcTex to PNG
    4. Exit
''')
    try:
        select = int(input("Select an option: "))
        if select == 1:
            imagePath = Path(input(f"Enter Canvas/UgcTex filepath: ").strip())
            with open(imagePath, 'rb') as file:
                rawdata = file.read()
                if len(rawdata) == 262144:
                    print('Canvas file detected.')
                    canvas_2_png(rawdata)
                elif len(rawdata) == 131072:
                    print('UgcTex file detected.')
                    ugctex_2_png(rawdata)
                else:
                    print('Size of file does not match Canvas nor UgcTex files. Please check your file again.')
        elif select ==2:
            imagePath = Path(input("Enter png filepath: ").strip())
            useSrgb = False
            while True:
                miitopi = input("Is your image ripped from Miitopia? This means it is in sRGB. (Y/N)")
                if miitopi.upper() == 'Y':
                    useSrgb = True
                    break
                elif miitopi.upper() == 'N':
                    break
                else:
                    print('Invalid input...Try that again.')

            while True:
                try:
                    png2type = int(input("What file will you convert this png to?\n1. Canvas\n2. UgcTex\nSelect an option: "))
                    if png2type == 1:
                        png_2_canvas(imagePath,useSrgb)
                        break
                    elif png2type == 2:
                        png_2_ugctex(imagePath,useSrgb)
                        break
                    else:
                        print("Invalid input...Let's try that again...")
                except ValueError:
                    print("Invalid input...Let's try that again...")
        elif select == 4:
            print('Alright, see ya~')
            break
        elif select == 3:
            direct = Path(input('Enter directiory: '))
            for f in direct.iterdir():
                imagePath = f
                if f.is_file():
                    with open(f, 'rb') as file:
                        rawdata = file.read()
                        if len(rawdata) == 262144:
                            print('Canvas file detected.')
                            canvas_2_png(rawdata)
                        elif len(rawdata) == 131072:
                            print('UgcTex file detected.')
                            ugctex_2_png(rawdata)
                        else:
                            print(f'Size of {file.name} does not match Canvas nor UgcTex files. Please check your file again.')
                
    except ValueError as e:
        print(e)
        print('woah man can you input a number please?')