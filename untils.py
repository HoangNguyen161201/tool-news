import google.generativeai as genai
import asyncio
import edge_tts
import cv2
import requests
import numpy as np
from moviepy.editor import ColorClip, vfx, VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import os

def generate_content(content):
    genai.configure(api_key="AIzaSyArae1nyjhAiRedUMkrUWd7p_-BJglXBNU")
    model = genai.GenerativeModel('gemini-1.0-pro-latest')
    response = model.generate_content(content)
    return response.text

def generate_to_voice(content, path):
    async def main() -> None:
        c = edge_tts.Communicate(content, 'vi-VN-HoaiMyNeural', rate="+10%", pitch="+20Hz")
        await c.save(path)
    asyncio.run(main())

def generate_image(link, out_path, out_blur_path):
    response = requests.get(link)
    if response.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(response.content)
    else:
        print("Yêu cầu không thành công. Mã trạng thái:", response.status_code)

    image = cv2.imread(out_path)
    image = cv2.flip(image, 1)
    image = image[50:-50, 50:-50]

    border_thickness = 10
    border_color = (255, 255, 255)
    image = cv2.copyMakeBorder(image, border_thickness, border_thickness, border_thickness, border_thickness, cv2.BORDER_CONSTANT, value=border_color)

    # Làm mờ hình ảnh bằng Blur
    blurred_image = cv2.GaussianBlur(image, (0, 0), 15)

    cv2.imwrite(out_path, image)
    cv2.imwrite(out_blur_path, blurred_image)

def generate_video_by_image(zoom_in, in_path, blur_in_path, out_path, second):
    clip_image = ImageClip(in_path).set_duration(second)
    clip_blurred_image = ImageClip(blur_in_path, duration= second).resize((1920, 1080))
    clip_blurred_image = clip_blurred_image.resize(lambda t: 1 + 0.3 * t/second)

    if not zoom_in:
        w_clip_image, h_clip_image = clip_image.size
        percent = (960 / w_clip_image) if (960 / w_clip_image) * h_clip_image < 720 else (720 / h_clip_image)
        clip_image = clip_image.resize((percent * w_clip_image, percent * h_clip_image))
        clip_image = clip_image.resize(lambda t: 1 + 0.4 * t/second)
    else:
        w_clip_image, h_clip_image = clip_image.size
        percent = ((1920 - 60) / w_clip_image) if ((1920 - 60) / w_clip_image) * h_clip_image < 1020 else (1020 / h_clip_image)
        clip_image = clip_image.resize((percent * w_clip_image, percent * h_clip_image))
        clip_image = clip_image.resize(lambda t: 1 - 0.3 * t/second)
    

    final_clip = CompositeVideoClip([clip_blurred_image.set_position('center'), clip_image.set_position('center')])

    final_clip.write_videofile(out_path, fps=24)

def concact_content_videos(audio_path, video_path_list, out_path):
    # Load âm thanh
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    duration_video = 0
    index = 0
    videos = [] 

    while duration_video < audio_duration:
        video = VideoFileClip(video_path_list[index])
        if(duration_video + video.duration > audio_duration):
            duration_end_video =  duration_video + video.duration - audio_duration
            video = video.subclip(0, duration_end_video)
            duration_video += duration_end_video
        else:
            duration_video += video.duration
        videos.append(video)
        if(index + 1 == video_path_list.__len__()):
            index = 0
        else:
            index += 1

    # Nối video lại với nhau
    final_video = concatenate_videoclips(videos)
    # Ghép video và âm thanh lại với nhau
    final_video = final_video.set_audio(audio)

    # Tạo avatar clip
    avatar_clip = ImageClip('./public/avatar.png').resize((200, 200))
    avatar_clip = avatar_clip.set_opacity(0.5)
    avatar_clip = avatar_clip.set_position((1550,  50))

    # add gif
    gif = VideoFileClip('./public/main_1.gif', has_mask= True)
    gif = gif.set_duration(duration_video)
    
    final_video = CompositeVideoClip([final_video, avatar_clip.set_duration(audio_duration), gif],)
    final_video.write_videofile(out_path)

    final_video.close()


def count_folders(path):
    # Kiểm tra xem đường dẫn tồn tại không
    if not os.path.exists(path):
        print("Đường dẫn không tồn tại")
        return
    
    # Đếm số lượng thư mục
    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    return len(folders)