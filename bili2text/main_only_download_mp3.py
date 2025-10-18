import argparse
from download_utils import download_video
from exAudio import batch_extract_and_split_audio  
from speech2text import load_whisper, run_analysis


def build_arg_parser():
    
    parser = argparse.ArgumentParser(
        description="B站视频批量处理工具：自动完成「视频下载→音频提取→语音转文字」全流程",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # 自动显示默认值
    )

    parser.add_argument(
        "--av",
        type=str,
        nargs="+",  # 支持接收1个及以上BV号
        required=True,
        help="需要处理的B站BV号，多个BV号用空格分隔（示例：--av BV1ZNr4YUE8Z BV123456）"
    )

    parser.add_argument(
        "--download-dir",
        type=str,
        default="/home/dale/yibiao.zhou/Bili_STT/downloaded_data",
        help="视频及后续音频、文本文件的保存根目录"
    )

    parser.add_argument(
        "--whisper-model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large"], 
        default="medium",
        help="Whisper语音识别模型大小，精度：tiny<base<small<medium<large，速度相反"
    )

    parser.add_argument(
        "--slice-length",
        type=int,
        default=45000,
        help="音频分割的单段长度（单位：毫秒），默认45000ms（45秒），适配多数API长度限制"
    )

    parser.add_argument(
        "--asr-prompt",
        type=str,
        default="以下是普通话的句子，内容可能包含生活话题、文化讨论，用词口语化。",
        help="Whisper转文字的初始提示词，用于优化特定场景的识别准确率"
    )

    # 解析参数并返回
    return parser.parse_args()


def main():
    args = build_arg_parser()

    print("=" * 60)
    print("当前处理配置：")
    print(f"• 待处理BV号列表：{args.av}")
    print(f"• 下载与输出根目录：{args.download_dir}")
    print(f"• Whisper模型：{args.whisper_model}")
    print(f"• 音频切片长度：{args.slice_length}ms")
    print(f"• ASR提示词：{args.asr_prompt}")
    print("=" * 60)

    av_list = args.av  
    download_dir = args.download_dir
    whisper_model = args.whisper_model

    # print(f"正在加载Whisper模型：{whisper_model}")
    # load_whisper(model=whisper_model)
    print("=" * 50)

    all_txt_files = []  
    for idx, av in enumerate(av_list, 1):
        try:
            downloaded_files = download_video(
                av[2:], 
                download_dir=download_dir,
                platform="bilibili"
            )
            if not downloaded_files:
                print(f"警告：BV号{av}未下载到视频文件，跳过后续处理")
                continue
        except Exception as e:
            print(f"错误：下载BV号{av}失败，原因：{str(e)}")
            continue

        try:
            batch_extract_and_split_audio(downloaded_files, False)

        except Exception as e:
            print(f"错误：BV号{av}音频处理失败，原因：{str(e)}")
            continue


if __name__ == "__main__":
    main()

