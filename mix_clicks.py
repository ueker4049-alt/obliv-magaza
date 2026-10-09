import numpy as np
import wave, struct, math

# 1. Load insta_music.wav
wf = wave.open('insta_music.wav', 'rb')
sr = wf.getframerate()
n_channels = wf.getnchannels()
n_frames = wf.getnframes()
music_raw = wf.readframes(n_frames)
wf.close()

music_data = np.frombuffer(music_raw, dtype=np.int16).reshape(-1, n_channels)
print(f"Music loaded: {len(music_data)} samples, {len(music_data)/sr:.2f}s, channels: {n_channels}")

# 2. Synthesize crisp, punchy tactile "tik" shutter / switch sound
# A combination of high frequency pop (2.5kHz -> 800Hz) and snap
click_len = int(sr * 0.04) # 40ms
t = np.linspace(0, 0.04, click_len, endpoint=False)
click_wave = (
    0.6 * np.sin(2 * np.pi * (2800 - t * 35000) * t) * np.exp(-t / 0.005) +
    0.4 * np.sin(2 * np.pi * 1200 * t) * np.exp(-t / 0.012) +
    0.2 * (np.random.rand(click_len) * 2 - 1) * np.exp(-t / 0.003)
)
click_wave = (click_wave / np.max(np.abs(click_wave)) * 28000).astype(np.int16)

# 3. Cut timestamps in seconds (matching the reference video beat rhythm)
# Distinct cuts:
cut_times = [
    0.0, 0.533, 0.700, 0.867, 1.033, 1.200, 1.367, 1.533, 1.867, 2.033,
    2.533, 2.700, 2.867, 3.200, 3.367, 3.700, 4.200, 4.533, 4.700, 4.867,
    5.033, 5.367, 5.533, 5.867, 6.033, 6.200, 6.533, 6.700, 6.867, 7.033,
    7.367, 7.533, 7.867, 8.367, 8.533, 8.700, 9.200, 9.367, 9.700, 9.867,
    10.033, 10.200, 10.367, 10.533, 10.700, 10.867
]

# Create output audio array (float for clean mixing)
mixed = music_data.astype(np.float32).copy()

for ct in cut_times:
    if ct == 0.0:
        continue # skip first frame start
    idx = int(ct * sr)
    if idx + click_len <= len(mixed):
        for ch in range(n_channels):
            mixed[idx : idx + click_len, ch] += click_wave * 0.95

# Clip and convert to int16
mixed = np.clip(mixed, -32767, 32767).astype(np.int16)

# Save mixed audio
out_wf = wave.open('insta_music_with_clicks.wav', 'wb')
out_wf.setnchannels(n_channels)
out_wf.setsampwidth(2)
out_wf.setframerate(sr)
out_wf.writeframes(mixed.tobytes())
out_wf.close()

print(f"Saved insta_music_with_clicks.wav successfully with {len(cut_times)-1} tik transitions!")
