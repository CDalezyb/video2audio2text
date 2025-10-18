import os
import re
import subprocess
import glob

def download_video(bv_number, download_dir="bilibili_video", platform="bilibili"):
    """
    使用you-get下载B站视频。
    参数:
        bv_number: 字符串形式的BV号（不含"BV"前缀）或完整BV号
    返回:
        文件路径列表
    """
    if platform == "bilibili":
        if not bv_number.startswith("BV"):
            bv_number = "BV" + bv_number
        video_url = f"https://www.bilibili.com/video/{bv_number}"
    else:
        raise ValueError("目前仅支持B站视频下载。")
    
    # 原始文件夹路径（仅包含BV号）
    original_dir = os.path.join(download_dir, bv_number)
    os.makedirs(original_dir, exist_ok=True)
    
    try:
        result = subprocess.run(["you-get", "-l", "-o", original_dir, video_url], capture_output=True, text=True)
        if result.returncode != 0:
            print("下载失败:", result.stderr)
            return []
        
        # 获取下载的视频文件
        video_files = glob.glob(os.path.join(original_dir, "*.mp4"))
        if not video_files:
            print("未找到下载的视频文件")
            return []
        
        # 删除xml文件
        xml_files = glob.glob(os.path.join(original_dir, "*.xml"))
        for xml_file in xml_files:
            os.remove(xml_file)
        
        # 从第一个视频文件中提取视频名称
        first_video = video_files[0]
        video_name = os.path.splitext(os.path.basename(first_video))[0]
        
        # 构建新的文件夹路径（BV号-视频名）
        new_dir_name = f"{bv_number}-{video_name}"
        new_dir_path = os.path.join(download_dir, new_dir_name)
        
        # 如果新文件夹已存在则先删除
        if os.path.exists(new_dir_path):
            import shutil
            shutil.rmtree(new_dir_path)
        
        # 重命名文件夹
        os.rename(original_dir, new_dir_path)
        print(f"文件夹已重命名为: {new_dir_path}")
        
        # 更新视频文件路径列表（指向新文件夹）
        updated_video_files = [os.path.join(new_dir_path, os.path.basename(f)) for f in video_files]
        return updated_video_files
        
    except Exception as e:
        print("发生错误:", str(e))
        return []