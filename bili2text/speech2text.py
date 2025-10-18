import whisper
import os

# ------------------------------
# Whisper 语音识别相关函数（适配新路径）
# ------------------------------
whisper_model = None

def is_cuda_available():
    return whisper.torch.cuda.is_available()

def load_whisper(model="tiny"):
    global whisper_model
    whisper_model = whisper.load_model(model, device="cuda" if is_cuda_available() else "cpu")
    print(f"Whisper模型加载完成：{model}")

def run_analysis(slice_dirs, prompt="以下是普通话的句子。"):
    """
    对切片文件夹中的音频进行批量转写
    :param slice_dirs: 切片文件夹路径列表（如[/home/.../BV1ZNr4YUE8Z/slices]）
    :return: 所有生成的文本文件路径组成的列表
    """
    global whisper_model
    if whisper_model is None:
        print("正在加载Whisper模型...")
        load_whisper()  # 默认加载tiny模型
    
    output_txt_list = []  # 存储所有生成的文本文件路径
    print("开始转换文本...")
    
    for slice_dir in slice_dirs:
        # 1. 解析路径：获取MP3文件所在目录（slices的父目录，即BV1ZNr4YUE8Z文件夹）
        mp3_parent_dir = os.path.dirname(slice_dir)  # 示例结果：/home/dale/.../BV1ZNr4YUE8Z
        
        # 2. 找到目录中唯一的MP3文件（与视频同名）
        mp3_files = [f for f in os.listdir(mp3_parent_dir) if f.endswith(".mp3")]
        if not mp3_files:
            print(f"警告：在 {mp3_parent_dir} 中未找到MP3文件，跳过该目录")
            continue
        # 取第一个MP3文件（按目录结构假设唯一，与视频同名）
        mp3_filename = mp3_files[0]
        # 生成文本文件路径：与MP3同目录、同名，后缀改为.txt
        output_txt = os.path.join(mp3_parent_dir, f"{os.path.splitext(mp3_filename)[0]}.txt")
        
        # 3. 获取并排序切片文件（按数字序号）
        audio_files = sorted(
            [f for f in os.listdir(slice_dir) if f.endswith(".mp3")],
            key=lambda x: int(os.path.splitext(x)[0])
        )
        
        if not audio_files:
            print(f"警告：切片文件夹 {slice_dir} 中未找到音频文件，跳过")
            continue
        
        # 4. 清空文本文件（避免多次运行重复写入）
        with open(output_txt, "w", encoding="utf-8") as f:
            pass
        
        # 5. 批量转写切片音频并写入文本文件
        for i, fn in enumerate(audio_files, 1):
            audio_path = os.path.join(slice_dir, fn)
            print(f"正在转换第{i}/{len(audio_files)}个音频... {audio_path}")
            
            # 调用Whisper转写，传入普通话提示提升准确率
            result = whisper_model.transcribe(audio_path, initial_prompt=prompt)
            # 提取并拼接所有片段文本
            text = "".join([seg["text"] for seg in result["segments"]])
            
            # 追加到文本文件
            with open(output_txt, "a", encoding="utf-8") as f:
                f.write(text + "\n")
        
        print(f"文本转写完成，结果保存于：{output_txt}")
        output_txt_list.append(output_txt)  # 收集文本文件路径
    
    return output_txt_list  # 返回所有生成的文本文件路径列表


# 使用示例
if __name__ == "__main__":
    # 示例切片文件夹路径（对应实际的slices目录）
    sample_slice_dirs = [
        "/home/dale/yibiao.zhou/Bili_STT/downloaded_data/BV1ZNr4YUE8Z/slices"
    ]
    
    # 加载模型（可根据需求切换为base/small等模型，精度更高但速度更慢）
    load_whisper(model="base")
    # 执行转写并获取生成的文本文件列表
    generated_txts = run_analysis(sample_slice_dirs)
    
    # 打印结果
    print("\n所有生成的文本文件：")
    for txt_path in generated_txts:
        print(txt_path)