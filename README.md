# ComfyUI-LoadAudioMulti

`LoadAudioMulti` 是一个独立的 ComfyUI 音频加载节点，用于在一个节点中一次加载多个音频或视频文件。

## 1. 项目解决什么问题

ComfyUI 自带的 `Load Audio` 节点通常一次只能选择一个音频文件。当工作流需要同时读取多个配音、人声、背景音乐或视频音轨时，需要重复放置多个加载节点，节点连线较多，管理和替换文件也不方便。

本项目的目标是：

- 用单个节点一次加载多个音频文件。
- 用一段文本集中管理所有文件名，方便复制、替换和批量修改。
- 同时提供音频列表和最多六个独立音频输出，兼顾批量处理和普通音频节点。

## 2. 主要功能

- 支持一次输入多个文件名。
- 文件名可以使用换行、逗号或空格分隔。
- 支持使用相对于 `ComfyUI/input` 目录的子目录路径，例如 `voice/audio1.wav`。
- 使用 PyAV 读取音频或视频文件中的第一条音频流。
- 支持 ComfyUI 中常见的音频和视频格式，具体取决于当前 PyAV 构建所包含的解码器。
- 输出全部音频组成的 `AUDIO` 列表，供支持列表输入的节点使用。
- 输出 `audio1` 至 `audio6` 六个独立音频，供普通音频节点直接连接。
- 输出加载后的完整文件路径，方便查看和调试。
- 音频统一转换为 `float32` PCM，并返回 ComfyUI 标准音频结构：

```python
{
    "waveform": waveform.unsqueeze(0),
    "sample_rate": sample_rate,
}
```

- 记录文件大小和修改时间，文件内容变化后可以触发节点重新执行。

## 3. 安装方法

###GitHub 安装 / 更新（推荐）

首次安装时，在 ComfyUI 的 custom_nodes 目录执行：

git clone https://github.com/haqia89/ComfyUI-LoadAudioMulti.git

### 方式一：手动安装

将整个 `ComfyUI-LoadAudioMulti` 文件夹放入 ComfyUI 的 `custom_nodes` 目录：

```text
ComfyUI/custom_nodes/ComfyUI-LoadAudioMulti/
```

目录中应包含：

```text
ComfyUI-LoadAudioMulti/
├── __init__.py
├── nodes.py
├── README.md
└── requirements.txt
```

### 安装依赖

本节点依赖 `av`。请在 ComfyUI 所使用的 Python 环境中安装：

```powershell
python -m pip install av
```

ComfyUI 便携版通常需要把 `python` 替换为整合包自带的 Python 可执行文件，例如：

```powershell
python_embeded\python.exe -m pip install av
```

部分整合包使用单独的 `python` 目录，例如：

```powershell
python\python.exe -m pip install av
```

### 启动 ComfyUI

安装完成后：

1. 完全关闭 ComfyUI。
2. 重新启动 ComfyUI。
3. 刷新浏览器页面。
4. 在节点菜单中确认可以找到 `Load Audios(input filenames)`。

## 4. 使用方法

### 准备音频文件

将音频或视频文件放入 ComfyUI 的 `input` 目录：

```text
ComfyUI/input/
```

例如：

```text
ComfyUI/input/voice1.wav
ComfyUI/input/voice2.mp3
ComfyUI/input/music/bgm.flac
```

### 添加节点

在 ComfyUI 节点菜单中找到：

```text
EasyAI/Audio/Load Audios(input filenames)
```

也可以在节点搜索框中搜索：

```text
Load Audios
```

或：

```text
LoadAudioMulti
```

### 输入文件名

在节点的 `filenames` 多行文本框中填写文件名。下面三种分隔方式都支持：

换行分隔：

```text
voice1.wav
voice2.mp3
music/bgm.flac
```

逗号分隔：

```text
voice1.wav, voice2.mp3, music/bgm.flac
```

空格分隔：

```text
voice1.wav voice2.mp3 music/bgm.flac
```

文件名应相对于 `ComfyUI/input` 目录。例如，实际文件位于：

```text
ComfyUI/input/music/bgm.flac
```

则应当填写：

```text
music/bgm.flac
```

### 输出说明

| 输出 | 类型 | 说明 |
| --- | --- | --- |
| `audios` | `AUDIO` 列表 | 包含本次成功加载的全部音频 |
| `filepaths` | `STRING` | 加载后的完整文件路径，每行一个 |
| `audio1` | `AUDIO` | 第 1 个音频 |
| `audio2` | `AUDIO` | 第 2 个音频 |
| `audio3` | `AUDIO` | 第 3 个音频 |
| `audio4` | `AUDIO` | 第 4 个音频 |
| `audio5` | `AUDIO` | 第 5 个音频 |
| `audio6` | `AUDIO` | 第 6 个音频 |

如果实际输入的文件少于六个，未加载的输出为 `None`。请不要连接这些没有对应音频的输出，否则下游节点可能报错。

### 连接示例

普通单音频节点可以直接连接前六个独立输出：

```text
Load Audios
├── audio1 -> Save Audio
├── audio2 -> Audio Preview
└── audio3 -> 其他 AUDIO 节点
```

需要一次处理全部音频时，可以将 `audios` 列表连接到支持列表输入的节点：

```text
Load Audios.audios -> 支持 AUDIO 列表输入的节点
```

### 常见问题

**节点没有出现在菜单中**

- 确认插件目录直接位于 `ComfyUI/custom_nodes` 下。
- 确认目录名称和层级正确，`__init__.py` 与 `nodes.py` 位于插件目录根部。
- 完全重启 ComfyUI，并检查启动日志中是否有加载错误。

**提示找不到 `av`**

确认 `av` 安装到了 ComfyUI 实际使用的 Python 环境中，而不是系统上的其他 Python。

**提示文件不存在**

文件名应相对于 `ComfyUI/input` 目录填写。检查文件名、扩展名和子目录路径是否正确。

**提示文件中没有音频流或无法解码**

- 视频文件必须包含音频流。
- 某些特殊编码需要 PyAV 构建中包含对应的解码器。
- 可以先用普通音频文件测试节点是否正常工作。
