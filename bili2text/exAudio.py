from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os
import subprocess
import whisper


# ------------------------------
# 音频提取与分割相关函数
# ------------------------------
def check_video_integrity(file_path):
    """使用 FFmpeg 验证视频文件完整性"""
    result = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', file_path, '-f', 'null', '-'],
        stderr=subprocess.PIPE,
        text=True
    )
    if result.stderr:
        print(f"视频文件可能损坏: {file_path}")
        print(f"FFmpeg 错误信息: {result.stderr}")
        return False
    return True


def batch_extract_and_split_audio(video_file_list,split_video:bool=True):
    """
    批量处理视频文件列表：提取音频并分割
    :param video_file_list: 本地视频文件名组成的列表（含路径）
    :return: 每个视频对应的切片文件夹（slices）的完整路径列表
    """
    slice_dirs = []  # 存储所有切片文件夹路径
    for video_path in video_file_list:
        video_dir = os.path.dirname(video_path)
        video_basename = os.path.splitext(os.path.basename(video_path))[0]
        
        # 提取音频并分割
        extract_audio_from_video(video_path, video_dir, video_basename)
        if not split_video:
            continue
        slice_dir = split_audio_into_slices(video_dir, video_basename)  # 获取当前视频的切片路径
        
        slice_dirs.append(slice_dir)
        print(f"视频 {video_basename} 处理完成，切片保存于：{slice_dir}")
    
    return slice_dirs  # 返回所有切片文件夹路径


def extract_audio_from_video(video_path, output_dir, audio_basename):
    """从单个视频文件中提取音频，保存为MP3（与视频同目录、同名）"""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")
    if not check_video_integrity(video_path):
        raise ValueError(f"视频文件损坏: {video_path}")
    
    audio_output_path = os.path.join(output_dir, f"{audio_basename}.mp3")
    
    with VideoFileClip(video_path) as clip:
        audio = clip.audio
        audio.write_audiofile(audio_output_path, codec="mp3")
    
    print(f"音频提取完成：{audio_output_path}")


def split_audio_into_slices(audio_dir, audio_basename, slice_length=45000, slice_dir_name="slices"):
    """
    将提取的音频分割为指定长度的片段，返回切片文件夹路径
    :return: 切片文件夹的完整路径
    """
    original_audio_path = os.path.join(audio_dir, f"{audio_basename}.mp3")
    if not os.path.exists(original_audio_path):
        raise FileNotFoundError(f"原始音频文件不存在: {original_audio_path}")
    
    # 切片文件夹路径（如：/home/.../BV1ZNr4YUE8Z/slices）
    slice_dir = os.path.join(audio_dir, slice_dir_name)
    os.makedirs(slice_dir, exist_ok=True)
    
    audio = AudioSegment.from_mp3(original_audio_path)
    total_slices = (len(audio) + slice_length - 1) // slice_length
    
    for i in range(total_slices):
        start = i * slice_length
        end = start + slice_length
        slice_audio = audio[start:end]
        slice_path = os.path.join(slice_dir, f"{i+1}.mp3")
        slice_audio.export(slice_path, format="mp3")
        print(f"音频片段 {i+1}/{total_slices} 保存：{slice_path}")
    
    return slice_dir  # 返回当前视频的切片文件夹路径


