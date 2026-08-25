import gradio as gr
import edge_tts
import asyncio
import requests
from PIL import Image
import moviepy.editor as mp
import os

VOICES = {
    "🇮🇳 বাংলা (পুরুষ - Pradeep)": "bn-IN-PradeepNeural",
    "🇮🇳 বাংলা (নারী - Tanishaa)": "bn-IN-TanishaaNeural",
    "🇮🇳 হিন্দি (পুরুষ - Madhur)": "hi-IN-MadhurNeural",
    "🇮🇳 হিন্দি (নারী - Swara)": "hi-IN-SwaraNeural",
    "🇺🇸 ইংরেজি (পুরুষ - Christopher)": "en-US-ChristopherNeural"
}

async def text_to_speech(text, voice, audio_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(audio_path)

def generate_video(prompt, reference_image, dialogue, voice_choice):
    try:
        image_path = "input_frame.jpg"
        if reference_image is not None:
            reference_image.save(image_path)
        else:
            image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=720&height=1280&nologo=true"
            response = requests.get(image_url)
            with open(image_path, "wb") as f:
                f.write(response.content)

        audio_path = "dialogue.mp3"
        voice_id = VOICES.get(voice_choice, "bn-IN-PradeepNeural")
        
        loop = asyncio.new_event_loop()
        asyncio.set_loop(loop) if hasattr(asyncio, "set_loop") else asyncio.set_event_loop(loop)
        loop.run_until_complete(text_to_speech(dialogue, voice_id, audio_path))

        try:
            from moviepy.editor import ImageClip, AudioFileClip
        except ImportError:
            from moviepy import ImageClip, AudioFileClip

        audio_clip = AudioFileClip(audio_path)
        duration = max(audio_clip.duration, 5.0)
        
        video_clip = ImageClip(image_path).set_duration(duration)
        video_clip = video_clip.set_audio(audio_clip)
        
        output_path = "final_output.mp4"
        video_clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        return output_path
    except Exception as e:
        print(f"Error: {e}")
        return None

custom_css = """
body {
    background-color: #0b0c10;
    color: #e5c158;
}
.gradio-container {
    background: linear-gradient(180deg, #121318 0%, #08080a 100%) !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.header-box {
    text-align: center;
    padding: 20px;
    background: radial-gradient(circle, rgba(212,175,55,0.15) 0%, rgba(0,0,0,0) 70%);
    border-bottom: 2px solid #d4af37;
    margin-bottom: 25px;
    border-radius: 15px;
}
.header-title {
    font-size: 28px;
    font-weight: 800;
    color: #f7d070;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 10px;
    text-shadow: 0px 2px 10px rgba(212,175,55,0.5);
}
.header-subtitle {
    font-size: 14px;
    color: #c5a059;
    letter-spacing: 1px;
}
.gold-card {
    background: #16181f !important;
    border: 1px solid #d4af37 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    padding: 15px !important;
}
.gold-btn {
    background: linear-gradient(45deg, #d4af37, #f7d070) !important;
    color: #000 !important;
    font-weight: bold !important;
    font-size: 16px !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(212,175,55,0.4) !important;
}
"""

with gr.Blocks(css=custom_css) as demo:
    with gr.Column(elem_classes="header-box"):
        gr.HTML("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="width: 90px; height: 90px; border-radius: 20px; border: 2px solid #d4af37; overflow: hidden; box-shadow: 0 0 20px rgba(212,175,55,0.4);">
                    <img src="https://i.ibb.co/hR5c2W7/gb-logo.png" style="width:100%; height:100%; object-fit: cover;" onerror="this.onerror=null; this.src='https://dummyimage.com/100x100/d4af37/000.png&text=GB';">
                </div>
                <div class="header-title">GB MOVIE CREATOR</div>
                <div class="header-subtitle">🎬 AI Cinematic Video Studio</div>
            </div>
        """)
    
    with gr.Row():
        with gr.Column(elem_classes="gold-card"):
            prompt_input = gr.Textbox(label="🎬 সিন বা অ্যাকশন প্রম্পট", placeholder="e.g. Hero fighting in rain, Bollywood style 4K")
            image_input = gr.Image(type="pil", label="📸 ক্যারেক্টার ফেস / রেফারেন্স ছবি")
            dialogue_input = gr.Textbox(label="🗣️ ডায়ালগ বা স্টোরি লাইন", placeholder="এখানে বাংলা বা হিন্দি ডায়ালগ লিখুন...")
            voice_dropdown = gr.Dropdown(choices=list(VOICES.keys()), value="🇮🇳 বাংলা (পুরুষ - Pradeep)", label="🎙️ ভয়েস ল্যাঙ্গুয়েজ সিলেক্ট করুন")
            generate_btn = gr.Button("🚀 Generate Video", elem_classes="gold-btn")
        
        with gr.Column(elem_classes="gold-card"):
            video_output = gr.Video(label="🎥 প্রিমিয়াম আউটপুট ভিডিও")

    generate_btn.click(
        fn=generate_video,
        inputs=[prompt_input, image_input, dialogue_input, voice_dropdown],
        outputs=video_output
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
