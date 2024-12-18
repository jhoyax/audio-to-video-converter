import os
import subprocess
import whisper

# Configuration
AUDIO_FILE = "assets/audio.mp3"  # Input audio file
BACKGROUND_VIDEO = "assets/minecraft_background.mp4"  # Background video file
OUTPUT_VIDEO = "assets/output_video.mp4"  # Output video file
CAPTIONS_FILE = "assets/captions.srt"  # Captions file

# Step 1: Transcribe Audio to Generate Captions
def transcribe_audio(audio_file):
    print("Transcribing audio...")
    model = whisper.load_model("base")  # Load the Whisper model
    result = model.transcribe(audio_file)

    # Create an SRT file for word-by-word captions
    with open(CAPTIONS_FILE, "w", encoding="utf-8") as srt_file:
        index = 1
        for segment in result["segments"]:
            start_time = segment["start"]
            end_time = segment["end"]
            words = segment["text"].split()  # Split the text into words
            duration = (end_time - start_time) / len(words)  # Duration per word

            # Assign timestamps to each word
            for i, word in enumerate(words):
                word_start = start_time + i * duration
                word_end = word_start + duration
                srt_file.write(
                    f"{index}\n{format_timestamp(word_start)} --> {format_timestamp(word_end)}\n{word}\n\n"
                )
                index += 1

    print(f"Word-by-word captions saved to {CAPTIONS_FILE}")
    return CAPTIONS_FILE

# Helper: Format timestamp for SRT
def format_timestamp(seconds):
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

# Step 2: Create Video with FFmpeg
def create_video(audio_file, background_video, captions_file, output_video):
    print("Creating video with FFmpeg...")
    command = [
        "ffmpeg",
        "-i", background_video,             # Input background video
        "-i", audio_file,                   # Input audio file
        "-vf", f"subtitles={captions_file}",# Add subtitles
        "-shortest",                        # Ensure video matches audio length
        "-c:v", "libx264",                  # Video codec
        "-c:a", "aac",                      # Audio codec
        "-y",                               # Overwrite output
        output_video                        # Output file
    ]
    subprocess.run(command, check=True)
    print(f"Video created: {output_video}")

# Main Function
def main():
    if not os.path.exists(AUDIO_FILE):
        print(f"Audio file '{AUDIO_FILE}' not found!")
        return
    
    if not os.path.exists(BACKGROUND_VIDEO):
        print(f"Background video '{BACKGROUND_VIDEO}' not found!")
        return
    
    # Transcribe the audio and generate captions
    transcribe_audio(AUDIO_FILE)
    
    # Create the final video
    create_video(AUDIO_FILE, BACKGROUND_VIDEO, CAPTIONS_FILE, OUTPUT_VIDEO)
    print("Process complete!")

if __name__ == "__main__":
    main()
