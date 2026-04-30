# TomoKoreTexTool

[English Version](README.md)

**朋友收集：梦想生活**（Tomodachi Life: Living the Dream）的纹理转换工具  
在游戏纹理格式（`.canvas`、`.ugctex`、`_Thumb.ugctex`）与 PNG 之间互转

本项目基于原作者 Timimimi 的 [TomoKoreFacepaintTool](https://github.com/Timimimi2/TomoKoreTexTool)使用AI进行了改进

免责声明：本软件仅限学习交流使用，禁止商业或者非法用途，否则后果自负
## 相比原版的改进

| 方面 | 改进 |
|---|---|
| **图片类型** | 支持 UgcFacePaint、UgcFood、UgcGoods 三种前缀（原版仅面部彩绘） |
| **文件编号** | 可选择 000–999 号文件编号，不再锁定单一编号 |
| **批量输出** | 一张 PNG 一次性生成全部三种格式（Canvas + UgcTex + Thumb） |
| **ZS 压缩** | 直接输出 `.zs` 格式，中间临时文件自动清理 |
| **保存位置** | 灵活的导出选项：默认路径、自定义路径、保留在当前位置。PNG 导出也有同款选择。 |
| **存储路径持久化** | 修改默认保存路径后重启脚本仍然生效，通过本地配置文件实现 |
| **路径自动清理** | 粘贴带双引号的文件路径时自动去除引号 |
| **正方形图片免询问** | 1:1 比例的图片自动拉伸缩放，仅非正方形图片弹出调整选项 |
| **动态 DDS 文件头** | 用 `make_dds_header()` 函数替代外部 `DDSHeader.ugctex` 二进制文件，适应任意分辨率和格式 |
| **灵活 UgcTex 解析** | 通过 block-grid 方式支持非 512×512 的 UgcTex 文件（如 384×512 的食物纹理） |
| **Gamma 修复** | 移除 Game→PNG 方向错误的 gamma 校正，解决输出图片泛白问题 |
| **中英双语界面** | 所有界面文字中英双语 |
| **Bug 修复** | 取消 resize 不再崩溃；批量模式取消 resize 正确处理；复制后原文件自动清理 |

## 支持格式

| 格式 | 分辨率 | 像素格式 | Alpha 支持 |
|---|---|---|---|
| `.canvas` | 256×256 | RGBA8（未压缩） | 完整 8 位 |
| `.ugctex` | 512×512* | DXT1 | 仅 1 位 |
| `_Thumb.ugctex` | 256×256 | DXT5 | 完整 8 位 |

\*部分食物纹理为 384×512，工具会自动识别处理。

## 环境要求

```bash
pip install pillow pyswizzle zstandard
```

## 使用方法

运行脚本：

```bash
python TomoKoreTexTool.py
```

### 主菜单

```
1. Canvas/UgcTex/Thumb 转 PNG
2. PNG 转 Canvas/UgcTex/Thumb
3. Miitopia PNG 转 Canvas/UgcTex/Thumb
4. 退出 (Exit)
```

### 选项 1：游戏格式 → PNG

1. 输入文件路径（支持 `.canvas`、`.ugctex`、`_Thumb.ugctex` 及 `.zs` 压缩版）
2. 选择 PNG 存放位置

### 选项 2：PNG → 游戏格式

1. 输入 PNG 文件路径
2. 选择图片类型：面部彩绘 / 食物 / 物品
3. 选择输出格式：
   - **Canvas+UgcTex+Thumb** — 一次性输出全部三种格式
   - **Canvas** — 仅 `.canvas`（256×256，RGBA8）
   - **UgcTex** — 仅 `.ugctex`（512×512，DXT1）
   - **Thumb** — 仅 `_Thumb.ugctex`（256×256，DXT5）
4. 输入文件编号（0–999）
5. 选择存放位置

### 选项 3：Miitopia PNG → 游戏格式

与选项 2 相同，但会应用 gamma 校正以适配来自 Miitopia 的图片。

### 缩放行为

当 PNG 尺寸与目标尺寸不匹配时：

- **正方形图片**（宽=高）— 自动拉伸，不弹出询问
- **非正方形图片** — 弹窗选择：拉伸 / 保持比例 / 取消

### 存档文件位置

游戏存档路径一般为：

```
%APPDATA%\..\..\user\save\0000000000000001\0\Ugc
```
将工具生成的文件导出到这个文件路径进行替换，进入游戏后即可生效

注：开始前请先对游戏的原文件进行备份防止意外

### 特别提醒

替换文件后启动游戏，会出现无法存档的问题：游戏内显示存档完成，但UTC文件夹内的文件并未更新。目前尚未找到故障原因，一种解决方法是打开任务管理器，重启Windows资源管理器，此后游戏即可正常存档。

## 许可证

本项目沿用原作者的许可证。详见[原始仓库](https://github.com/Timimimi2/TomoKoreTexTool)。

## 鸣谢

- **Timimimi** — 原作者
- **RealDarkCraft** — 文件格式逆向解析
- **Aclios** — [pyswizzle](https://github.com/Aclios/pyswizzle) 库
- **Pillow** — Python 图像处理库
