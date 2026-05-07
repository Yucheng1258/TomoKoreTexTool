try:
    from PIL import Image, ImageCms, ImageOps
    from pyswizzle import nsw_deswizzle, nsw_swizzle
    from pathlib import Path
    import io
    import json
    import struct
    import shutil
    import sys
    import zstandard as zstd
except ImportError as e:
    print(f"导入错误 (Import error)：{e}")


_DEFAULT_SAVE_PATH_1 = r"D:\ryujinx-canary-1.3.287-win_x64\publish\portable\bis\user\save\0000000000000001\0\Ugc"
_DEFAULT_SAVE_PATH_2 = r"D:\ryujinx-canary-1.3.287-win_x64\publish\portable\bis\user\save\0000000000000001\1\Ugc"
_APP_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
_CONFIG_FILE = _APP_DIR / '.tomokore_config.json'


def _load_config():
    try:
        with open(_CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
            return cfg.get('default_save_path', _DEFAULT_SAVE_PATH_1), cfg.get('default_save_path_2', _DEFAULT_SAVE_PATH_2)
    except (FileNotFoundError, json.JSONDecodeError):
        return _DEFAULT_SAVE_PATH_1, _DEFAULT_SAVE_PATH_2


def _save_config():
    with open(_CONFIG_FILE, 'w') as f:
        json.dump({'default_save_path': DEFAULT_SAVE_PATH_1, 'default_save_path_2': DEFAULT_SAVE_PATH_2}, f)


DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2 = _load_config()


def clean_path(s: str) -> str:
    """去除路径首尾空格及双引号"""
    return s.strip().strip('"')


def _clean_output_name(filepath: Path, suffix: str) -> str:
    """去除 .zs 和游戏格式扩展名后追加后缀"""
    name = filepath.name
    if name.endswith('.zs'):
        name = name[:-3]
    # 去除已知游戏格式扩展名
    for ext in ('.canvas', '.ugctex'):
        if name.endswith(ext):
            name = name[:-len(ext)]
            break
    return name + suffix


def gammaedit(img: Image, gamma=0.4545):
    return img.point(lambda x: ((x / 255) ** gamma) * 255)


def make_dds_header(w, h, fmt='DXT5'):
    """构建DDS文件头（128字节）"""
    header = bytearray(128)
    header[0:4] = b'DDS '
    struct.pack_into('<I', header, 4, 124)
    struct.pack_into('<I', header, 8, 0x000A1007)
    struct.pack_into('<I', header, 12, h)
    struct.pack_into('<I', header, 16, w)
    struct.pack_into('<I', header, 28, 1)
    struct.pack_into('<I', header, 76, 32)
    struct.pack_into('<I', header, 80, 4)
    header[84:88] = fmt.encode()
    struct.pack_into('<I', header, 108, 0x1000)
    return bytes(header)


def ask_image_type():
    """询问用户图片类型，返回前缀字符串"""
    while True:
        try:
            print('\n请选择图片类型 (Select image type)：')
            print('1. 面部彩绘 (UgcFacePaint)')
            print('2. 食物 (UgcFood)')
            print('3. 宝物 (UgcGoods)')
            choice = int(input('请选择 (Select an option)：'))
            if choice == 1:
                return 'UgcFacePaint'
            elif choice == 2:
                return 'UgcFood'
            elif choice == 3:
                return 'UgcGoods'
            else:
                print('请输入 1、2 或 3 (Please enter 1, 2, or 3)。')
        except ValueError:
            print('请输入数字 (Please input a number)。')


def ask_slot_number(prefix):
    """询问用户文件编号"""
    while True:
        try:
            num = int(input(f'\n请输入文件编号（0={prefix}000, 1={prefix}001, and so on / 以此类推）：'))
            if num < 0:
                print('请输入0或以上的数字 (Please enter 0 or above)。')
            else:
                return f'{num:03d}'
        except ValueError:
            print('请输入数字 (Please input a number)。')


def compress_to_zs(src_path: Path) -> Path:
    """将文件压缩为.zs格式，返回压缩后的路径"""
    zs_path = src_path.with_suffix(src_path.suffix + '.zs')
    cctx = zstd.ZstdCompressor(level=1)
    with open(src_path, 'rb') as f_in:
        data = f_in.read()
    with open(zs_path, 'wb') as f_out:
        f_out.write(cctx.compress(data))
    return zs_path


def ask_save_location(zs_path: Path, file_label: str):
    """询问用户zs文件的存放位置，返回 True 表示已复制到新位置"""
    global DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2
    print(f'\n{file_label} 已生成 (Generated)：{zs_path}')
    print(f'请选择 {file_label} 的存放位置 (Choose save location for {file_label})：')
    print('1. 导出到两个默认地址 (Export to both default paths)')
    print(f'   默认地址1 (Default path 1)：{DEFAULT_SAVE_PATH_1}')
    print(f'   默认地址2 (Default path 2)：{DEFAULT_SAVE_PATH_2}')
    print('2. 自定义路径 (Custom path)')
    print('3. 不移动，保留在当前位置 (Keep in current location)')
    print('4. 修改默认地址1 (Modify default path 1)')
    print('5. 修改默认地址2 (Modify default path 2)')
    while True:
        try:
            choice = int(input('请选择 (Select an option)：'))
            if choice == 1:
                for sp in (DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2):
                    dest_dir = Path(sp)
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest = dest_dir / zs_path.name
                    shutil.copy2(zs_path, dest)
                    print(f'已复制到 (Copied to)：{dest}')
                return True
            elif choice == 2:
                custom = clean_path(input('请输入目标文件夹路径 (Enter target folder path)：'))
                dest_dir = Path(custom)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / zs_path.name
                shutil.copy2(zs_path, dest)
                print(f'已复制到 (Copied to)：{dest}')
                return True
            elif choice == 3:
                print('文件保留在当前位置 (File kept in current location)。')
                return False
            elif choice == 4:
                new_path = clean_path(input('请输入新的默认地址1 (Enter new default path 1)：'))
                DEFAULT_SAVE_PATH_1 = new_path
                _save_config()
                print(f'默认地址1已更新为 (Default path 1 updated to)：{DEFAULT_SAVE_PATH_1}')
            elif choice == 5:
                new_path = clean_path(input('请输入新的默认地址2 (Enter new default path 2)：'))
                DEFAULT_SAVE_PATH_2 = new_path
                _save_config()
                print(f'默认地址2已更新为 (Default path 2 updated to)：{DEFAULT_SAVE_PATH_2}')
            else:
                print('请输入 1、2、3、4 或 5 (Please enter 1, 2, 3, 4, or 5)。')
        except ValueError:
            print('请输入数字 (Please input a number)。')


def ask_png_save_location(png_path: Path):
    """询问用户PNG文件的存放位置，返回 True 表示已复制到新位置"""
    global DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2
    print(f'\nPNG 已生成 (Generated)：{png_path.name}')
    print('请选择 PNG 的存放位置 (Choose save location for PNG)：')
    print('1. 导出到两个默认地址 (Export to both default paths)')
    print(f'   默认地址1 (Default path 1)：{DEFAULT_SAVE_PATH_1}')
    print(f'   默认地址2 (Default path 2)：{DEFAULT_SAVE_PATH_2}')
    print('2. 自定义路径 (Custom path)')
    print('3. 不移动，保留在当前位置 (Keep in current location)')
    print('4. 修改默认地址1 (Modify default path 1)')
    print('5. 修改默认地址2 (Modify default path 2)')
    while True:
        try:
            choice = int(input('请选择 (Select an option)：'))
            if choice == 1:
                for sp in (DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2):
                    dest_dir = Path(sp)
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest = dest_dir / png_path.name
                    shutil.copy2(png_path, dest)
                    print(f'已复制到 (Copied to)：{dest}')
                return True
            elif choice == 2:
                custom = clean_path(input('请输入目标文件夹路径 (Enter target folder path)：'))
                dest_dir = Path(custom)
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / png_path.name
                shutil.copy2(png_path, dest)
                print(f'已复制到 (Copied to)：{dest}')
                return True
            elif choice == 3:
                print('文件保留在当前位置 (File kept in current location)。')
                return False
            elif choice == 4:
                new_path = clean_path(input('请输入新的默认地址1 (Enter new default path 1)：'))
                DEFAULT_SAVE_PATH_1 = new_path
                _save_config()
                print(f'默认地址1已更新为 (Default path 1 updated to)：{DEFAULT_SAVE_PATH_1}')
            elif choice == 5:
                new_path = clean_path(input('请输入新的默认地址2 (Enter new default path 2)：'))
                DEFAULT_SAVE_PATH_2 = new_path
                _save_config()
                print(f'默认地址2已更新为 (Default path 2 updated to)：{DEFAULT_SAVE_PATH_2}')
            else:
                print('请输入 1、2、3、4 或 5 (Please enter 1, 2, 3, 4, or 5)。')
        except ValueError:
            print('请输入数字 (Please input a number)。')


def thumb_2_png(rawdata, imagePath):
    """将Thumb.ugctex（65536字节，256x256 DXT5）转换为PNG"""
    convertSize = (256, 256)
    block_grid = (64, 64)
    gob_w, gob_h = 1, 1
    bytes_per_block = 16
    swizzle_mode = 3
    swizzled = nsw_deswizzle(rawdata, block_grid, (gob_w, gob_h), bytes_per_block, swizzle_mode)
    dds = make_dds_header(convertSize[0], convertSize[1], 'DXT5') + bytes(swizzled)
    img = Image.open(io.BytesIO(dds)).convert('RGBA')
    img = gammaedit(img, 0.4545)
    savepath = imagePath.with_name(_clean_output_name(imagePath, '_OUTPUT.png'))
    img.save(savepath, 'png')
    print(f'图片已保存至 (Image saved to)：{savepath}')
    moved = ask_png_save_location(savepath)
    img.show()
    if moved:
        savepath.unlink()


def png_2_thumb(imagePath, useSrgb, prefix, ugc_num=None, skip_save=False):
    """将PNG转换为Thumb.ugctex（256x256 DXT5）"""
    imageRes = 0
    img = Image.open(imagePath)
    convertSize = (256, 256)
    if img.size != convertSize:
        if img.size[0] == img.size[1]:
            imageRes = 1
        else:
            while True:
                try:
                    print('''
                        图片分辨率不正确（应为 256x256）。
                        请选择处理方式 (Please select an option)：
                        --------------------------
                        1. 拉伸并调整大小 (Stretch and Resize)
                        2. 保持比例并调整大小 (Keep aspect ratio)
                        3. 取消 (Cancel)
                        ''')
                    imageRes = int(input('请选择 (Select an option)：'))
                    if 0 < imageRes < 4:
                        break
                    else:
                        print('输入无效，请输入 1 到 3 的数字 (Invalid input)。')
                except ValueError:
                    print('请输入数字 (Please input a number)。')

    if imageRes != 3:
        if imageRes == 1:
            img = img.resize(convertSize, 1)
        elif imageRes == 2:
            img = ImageOps.fit(img, convertSize)
        if not useSrgb:
            img = gammaedit(img, 2.2)

        dds_bytes = io.BytesIO()
        img.save(dds_bytes, format='DDS', pixel_format='DXT5')

        if ugc_num is None:
            ugc_num = ask_slot_number(prefix)
        thumb_filename = f'{prefix}{ugc_num}_Thumb.ugctex'
        savepath = imagePath.with_name(thumb_filename)

        block_grid = (64, 64)
        gob_w, gob_h = 1, 1
        bytes_per_block = 16
        swizzle_mode = 3
        bSlice = dds_bytes.getvalue()[128:]
        swizzled = nsw_swizzle(bSlice, block_grid, (gob_w, gob_h), bytes_per_block, swizzle_mode)

        with open(savepath, 'wb') as f:
            f.write(bytes(swizzled))
        print(f'Thumb 文件已保存 (Thumb file saved)：{savepath}')

        print('正在压缩为 .zs 格式 (Compressing to .zs format)...')
        zs_path = compress_to_zs(savepath)
        savepath.unlink()
        print(f'.zs 文件已生成 (.zs file generated)：{zs_path}')

        if not skip_save:
            moved = ask_save_location(zs_path, f'{prefix}{ugc_num}_Thumb.ugctex.zs')
            if moved:
                zs_path.unlink()
        return zs_path


def canvas_2_png(img):
    swizzle_mode = 4
    convertSize = (256, 256)
    gob_w, gob_h = 1, 1
    bytes_per_block = 4
    swizzled = nsw_deswizzle(rawdata, (convertSize[0], convertSize[1]), (gob_w, gob_h), bytes_per_block, swizzle_mode)
    if select == 1:
        img = Image.frombytes('RGBA', convertSize, swizzled, 'raw', 'RGBA')
    img = gammaedit(img, 0.4545)
    img = img.convert()
    savepath = imagePath.with_name(_clean_output_name(imagePath, 'CanvasOUTPUT.png'))
    img.save(savepath, 'png')
    moved = ask_png_save_location(savepath)
    img.show()
    if moved:
        savepath.unlink()
    return


def png_2_canvas(imagePath, useSrgb, prefix, ugc_num=None, skip_save=False):
    imageRes = 0
    img = Image.open(imagePath)
    if img.size != (256, 256):
        if img.size[0] == img.size[1]:
            imageRes = 1
        else:
            while True:
                try:
                    print('''
                        图片分辨率不正确（应为 256x256）。
                        请选择处理方式 (Please select an option)：
                        --------------------------
                        1. 拉伸并调整大小 (Stretch and Resize)
                        2. 保持比例并调整大小 (Keep aspect ratio)
                        3. 取消 (Cancel)
                        ''')
                    imageRes = int(input('请选择 (Select an option)：'))
                    if 0 < imageRes < 4:
                        break
                    else:
                        print('输入无效，请输入 1 到 3 的数字 (Invalid input)。')
                except ValueError:
                    print('请输入数字 (Please input a number)。')

    if imageRes != 3:
        if imageRes == 1:
            img = img.resize((256, 256), 1)
        elif imageRes == 2:
            img = ImageOps.fit(img, (256, 256))

        if not useSrgb:
            img = gammaedit(img, 2.2)
        img = img.convert('RGBA')
        convertImg = img.tobytes('raw')

        if ugc_num is None:
            ugc_num = ask_slot_number(prefix)
        canvas_filename = f'{prefix}{ugc_num}.canvas'
        savepath = imagePath.with_name(canvas_filename)

        gob_w, gob_h = 1, 1
        bytes_per_block = 4
        swizzle_mode = 4
        height, width = 256, 256
        linear = nsw_swizzle(convertImg, (width, height), (gob_w, gob_h), bytes_per_block, swizzle_mode)

        with open(savepath, 'wb') as f:
            f.write(bytes(linear))
        print(f'Canvas 文件已保存 (Canvas file saved)：{savepath}')

        # 压缩为.zs
        print('正在压缩为 .zs 格式 (Compressing to .zs format)...')
        zs_path = compress_to_zs(savepath)
        savepath.unlink()
        print(f'.zs 文件已生成 (.zs file generated)：{zs_path}')

        if not skip_save:
            moved = ask_save_location(zs_path, f'{prefix}{ugc_num}.canvas.zs')
            if moved:
                zs_path.unlink()
        return zs_path


def ugctex_2_png(img):
    bytes_per_block = 8
    swizzle_mode = 4
    total_blocks = len(rawdata) // bytes_per_block
    # 使用 block grid 方式 (gob=1) 适应不同分辨率
    # mode=4 要求 block grid 高度为 128 的倍数
    for try_h in range(128, total_blocks + 1, 128):
        if total_blocks % try_h == 0:
            block_h = try_h
            block_w = total_blocks // try_h
            break
    else:
        raise ValueError(f'无法解析 {len(rawdata)} 字节的 ugctex 文件 (Cannot parse ugctex file)')
    convertSize = (block_w, block_h)
    pixel_w, pixel_h = block_w * 4, block_h * 4
    ddsheader = make_dds_header(pixel_w, pixel_h, 'DXT1')
    swizzled = nsw_deswizzle(rawdata, convertSize, (1, 1), bytes_per_block, swizzle_mode)
    img = Image.open(io.BytesIO(ddsheader + swizzled))
    img = gammaedit(img, 0.4545)
    img = img.convert()
    savepath = imagePath.with_name(_clean_output_name(imagePath, 'UgcTexOUTPUT.png'))
    img.save(savepath, 'png')
    moved = ask_png_save_location(savepath)
    img.show()
    if moved:
        savepath.unlink()


def png_2_ugctex(imagePath, useSrgb, prefix, ugc_num=None, skip_save=False):
    imageRes = 0
    img = Image.open(imagePath)
    convertSize = (512, 512)
    if img.size != convertSize:
        if img.size[0] == img.size[1]:
            imageRes = 1
        else:
            while True:
                try:
                    print('''
                        图片分辨率不正确（应为 512x512）。
                        请选择处理方式 (Please select an option)：
                        --------------------------
                        1. 拉伸并调整大小 (Stretch and Resize)
                        2. 保持比例并调整大小 (Keep aspect ratio)
                        3. 取消 (Cancel)
                        ''')
                    imageRes = int(input('请选择 (Select an option)：'))
                    if 0 < imageRes < 4:
                        break
                    else:
                        print('输入无效，请输入 1 到 3 的数字 (Invalid input)。')
                except ValueError:
                    print('请输入数字 (Please input a number)。')

    if imageRes != 3:
        if imageRes == 1:
            img = img.resize(convertSize, 1)
        elif imageRes == 2:
            img = ImageOps.fit(img, convertSize)
        if not useSrgb:
            img = gammaedit(img, 2.2)

        dds_bytes = io.BytesIO()
        img.save(dds_bytes, format='DDS', pixel_format='DXT1')

        if ugc_num is None:
            ugc_num = ask_slot_number(prefix)
        ugctex_filename = f'{prefix}{ugc_num}.ugctex'
        savepath = imagePath.with_name(ugctex_filename)

        gob_w, gob_h = 4, 4
        bytes_per_block = 8
        swizzle_mode = 4
        bSlice = dds_bytes.getvalue()[128:]
        swizzled = nsw_swizzle(bSlice, convertSize, (gob_w, gob_h), bytes_per_block, swizzle_mode)

        with open(savepath, 'wb') as f:
            f.write(bytes(swizzled))
        print(f'UgcTex 文件已保存 (UgcTex file saved)：{savepath}（透明度可能变为不透明 / transparency may become opaque）')

        # 压缩为.zs
        print('正在压缩为 .zs 格式 (Compressing to .zs format)...')
        zs_path = compress_to_zs(savepath)
        savepath.unlink()
        print(f'.zs 文件已生成 (.zs file generated)：{zs_path}')

        if not skip_save:
            moved = ask_save_location(zs_path, f'{prefix}{ugc_num}.ugctex.zs')
            if moved:
                zs_path.unlink()
        return zs_path


def png_conversion_flow(imagePath, useSrgb):
    global DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2
    prefix = ask_image_type()
    while True:
        try:
            is_facepaint = prefix == 'UgcFacePaint'
            if is_facepaint:
                menu_text = ("要将 PNG 转换为何种格式？(Convert to which format?)\n"
                             "1. Canvas+UgcTex\n2. Canvas\n3. UgcTex\n"
                             "请选择 (Select an option)：")
                max_opt = 3
            else:
                menu_text = ("要将 PNG 转换为何种格式？(Convert to which format?)\n"
                             "1. Canvas+UgcTex+Thumb\n2. Canvas\n3. UgcTex\n4. Thumb\n"
                             "请选择 (Select an option)：")
                max_opt = 4
            png2type = int(input(menu_text))
            if png2type == 1:
                ugc_num = ask_slot_number(prefix)
                zs_paths = []
                zs_paths.append(png_2_canvas(imagePath, useSrgb, prefix, ugc_num, skip_save=True))
                zs_paths.append(png_2_ugctex(imagePath, useSrgb, prefix, ugc_num, skip_save=True))
                if not is_facepaint:
                    zs_paths.append(png_2_thumb(imagePath, useSrgb, prefix, ugc_num, skip_save=True))
                zs_paths = [p for p in zs_paths if p is not None]
                if zs_paths:
                    print(f'\n全部 .zs 文件已生成 (All .zs files generated)')
                    print('请选择存放位置 (Choose save location)：')
                    print('1. 导出到两个默认地址 (Export to both default paths)')
                    print(f'   默认地址1 (Default path 1)：{DEFAULT_SAVE_PATH_1}')
                    print(f'   默认地址2 (Default path 2)：{DEFAULT_SAVE_PATH_2}')
                    print('2. 自定义路径 (Custom path)')
                    print('3. 不移动，保留在当前位置 (Keep in current location)')
                    print('4. 修改默认地址1 (Modify default path 1)')
                    print('5. 修改默认地址2 (Modify default path 2)')
                    while True:
                        try:
                            batch_choice = int(input('请选择 (Select an option)：'))
                            if batch_choice == 1:
                                for sp in (DEFAULT_SAVE_PATH_1, DEFAULT_SAVE_PATH_2):
                                    dest_dir = Path(sp)
                                    dest_dir.mkdir(parents=True, exist_ok=True)
                                    for p in zs_paths:
                                        dest = dest_dir / p.name
                                        shutil.copy2(p, dest)
                                        print(f'已复制到 (Copied to)：{dest}')
                                for p in zs_paths:
                                    p.unlink()
                                break
                            elif batch_choice == 2:
                                custom = clean_path(input('请输入目标文件夹路径 (Enter target folder path)：'))
                                dest_dir = Path(custom)
                                dest_dir.mkdir(parents=True, exist_ok=True)
                                for p in zs_paths:
                                    dest = dest_dir / p.name
                                    shutil.copy2(p, dest)
                                    print(f'已复制到 (Copied to)：{dest}')
                                    p.unlink()
                                break
                            elif batch_choice == 3:
                                print('文件保留在当前位置 (File kept in current location)。')
                                break
                            elif batch_choice == 4:
                                new_path = clean_path(input('请输入新的默认地址1 (Enter new default path 1)：'))
                                DEFAULT_SAVE_PATH_1 = new_path
                                _save_config()
                                print(f'默认地址1已更新为 (Default path 1 updated to)：{DEFAULT_SAVE_PATH_1}')
                            elif batch_choice == 5:
                                new_path = clean_path(input('请输入新的默认地址2 (Enter new default path 2)：'))
                                DEFAULT_SAVE_PATH_2 = new_path
                                _save_config()
                                print(f'默认地址2已更新为 (Default path 2 updated to)：{DEFAULT_SAVE_PATH_2}')
                            else:
                                print('请输入 1、2、3、4 或 5 (Please enter 1, 2, 3, 4, or 5)。')
                        except ValueError:
                            print('请输入数字 (Please input a number)。')
                break
            elif png2type == 2:
                png_2_canvas(imagePath, useSrgb, prefix)
                break
            elif png2type == 3:
                png_2_ugctex(imagePath, useSrgb, prefix)
                break
            elif png2type == 4 and max_opt == 4:
                png_2_thumb(imagePath, useSrgb, prefix)
                break
            else:
                print("输入无效，请重试 (Invalid input, try again)。")
        except ValueError:
            print("输入无效，请重试 (Invalid input, try again)。")


print('''
  TomoKoreTexTool
  朋友收集：梦想生活  纹理转换工具
  Tomodachi Life: Living the Dream  Texture Converter

  原作者 / Original: Timimimi  ·  改进 / Mods: Yucheng1258
      
  免责声明：本软件仅限学习交流使用，禁止商业或者非法用途，否则后果自负
  Disclaimer: 
  This software is for learning and exchange purposes only. 
  It is prohibited to use it for commercial or illegal purposes. 
  Any consequences arising therefrom shall be borne by the user.    
''')

while True:
    print('''
    -------
    功能 (Functions)
    -------
    1. Canvas/UgcTex/Thumb 转 PNG
    2. PNG 转 Canvas/UgcTex/Thumb
    3. Miitopia PNG 转 Canvas/UgcTex/Thumb
    4. 退出 (Exit)
''')
    try:
        select = int(input("请选择 (Select an option)："))
        if select == 1:
            imagePath = Path(clean_path(input(f"请输入 Canvas/UgcTex/Thumb 文件路径 (Enter filepath)：")))
            with open(imagePath, 'rb') as file:
                rawdata = file.read()
            if imagePath.suffix == '.zs':
                rawdata = zstd.ZstdDecompressor().decompress(rawdata)
            if len(rawdata) == 262144:
                print('检测到 Canvas 文件 (Canvas file detected)。')
                canvas_2_png(rawdata)
            elif len(rawdata) in (131072, 98304):
                print('检测到 UgcTex 文件 (UgcTex file detected)。')
                ugctex_2_png(rawdata)
            elif len(rawdata) == 65536:
                print('检测到 Thumb.ugctex 文件 (Thumb.ugctex file detected)。')
                thumb_2_png(rawdata, imagePath)
            else:
                print('文件大小不匹配 Canvas、UgcTex 或 Thumb 文件，请检查文件 (File size does not match)。')
        elif select == 2:
            imagePath = Path(clean_path(input("请输入 PNG 文件路径 (Enter png filepath)：")))
            png_conversion_flow(imagePath, False)
        elif select == 3:
            imagePath = Path(clean_path(input("请输入 Miitopia PNG 文件路径 (Enter Miitopia png filepath)：")))
            png_conversion_flow(imagePath, True)
        elif select == 4:
            print('再见 (See ya)~')
            break
        else:
            print('输入无效，请输入 1 到 4 的数字 (Invalid input, please enter 1-4)。')
    except ValueError as e:
        print(e)
        print('请输入数字 (Please input a number)。')
