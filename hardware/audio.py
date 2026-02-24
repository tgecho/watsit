import subprocess


class AudioPlayer:
    def play(self, filename: str):
        if filename.endswith(".mp3"):
            subprocess.run(["mpg123", "-q", filename], capture_output=True)
        else:
            subprocess.run(["aplay", filename], capture_output=True)


class MockAudioPlayer:
    def play(self, filename: str):
        print(f"[AUDIO] {filename}")
