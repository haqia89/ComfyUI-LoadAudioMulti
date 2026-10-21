import os
import re

import av
import folder_paths
import torch


def _split_filenames(filenames):
    return [
        filename.strip()
        for filename in re.split(r"[, \r\n]+", filenames)
        if filename.strip()
    ]


def _f32_pcm(wav):
    """将音频张量转换为 float32 PCM。"""
    if wav.dtype.is_floating_point:
        return wav
    if wav.dtype == torch.int16:
        return wav.float() / (2 ** 15)
    if wav.dtype == torch.int32:
        return wav.float() / (2 ** 31)
    raise ValueError(f"不支持的音频数据类型: {wav.dtype}")


def _load_audio_file(filepath):
    """读取音频或视频文件中的第一条音频流。"""
    with av.open(filepath) as af:
        if not af.streams.audio:
            raise ValueError(f"文件中没有音频流: {filepath}")

        stream = af.streams.audio[0]
        sample_rate = stream.codec_context.sample_rate
        channel_count = stream.channels

        frames = []
        for frame in af.decode(streams=stream.index):
            buf = torch.from_numpy(frame.to_ndarray())
            if buf.shape[0] != channel_count:
                buf = buf.view(-1, channel_count).t()
            frames.append(buf)

        if not frames:
            raise ValueError(f"未能解码音频: {filepath}")

        waveform = torch.cat(frames, dim=1)
        return _f32_pcm(waveform), sample_rate


class LoadAudioMulti:
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        os.makedirs(input_dir, exist_ok=True)

        return {
            "required": {
                "filenames": (
                    "STRING",
                    {
                        "default": "audio1.wav\naudio2.mp3",
                        "tooltip": "输入多个音频或视频文件名，用逗号、空格或换行分隔。",
                        "multiline": True,
                    },
                ),
            }
        }

    CATEGORY = "EasyAI/Audio"
    RETURN_TYPES = (
        "AUDIO",
        "STRING",
        "AUDIO",
        "AUDIO",
        "AUDIO",
        "AUDIO",
        "AUDIO",
        "AUDIO",
    )
    RETURN_NAMES = (
        "audios",
        "filepaths",
        "audio1",
        "audio2",
        "audio3",
        "audio4",
        "audio5",
        "audio6",
    )
    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (True, False, False, False, False, False, False, False)
    FUNCTION = "load_audios"

    @classmethod
    def IS_CHANGED(cls, filenames):
        signature = []
        for filename in _split_filenames(filenames):
            filepath = folder_paths.get_annotated_filepath(filename)
            try:
                stat = os.stat(filepath)
                signature.append(
                    f"{filepath}:{stat.st_size}:{stat.st_mtime_ns}"
                )
            except OSError:
                signature.append(filename)
        return "|".join(signature)

    def load_audios(self, filenames):
        filenames = _split_filenames(filenames)

        if not filenames:
            raise ValueError("未提供有效的音频文件名，请至少输入一个文件名。")

        output_audios = []
        output_paths = []

        for filename in filenames:
            filepath = folder_paths.get_annotated_filepath(filename)

            if not folder_paths.exists_annotated_filepath(filename):
                raise FileNotFoundError(f"文件不存在: {filename}")

            waveform, sample_rate = _load_audio_file(filepath)
            output_audios.append(
                {
                    "waveform": waveform.unsqueeze(0),
                    "sample_rate": sample_rate,
                }
            )
            output_paths.append(filepath)

        single_audios = [
            output_audios[index] if index < len(output_audios) else None
            for index in range(6)
        ]

        return (
            output_audios,
            "\n".join(output_paths),
            *single_audios,
        )


NODE_CLASS_MAPPINGS = {
    "LoadAudioMulti": LoadAudioMulti,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadAudioMulti": "Load Audios(input filenames)",
}
