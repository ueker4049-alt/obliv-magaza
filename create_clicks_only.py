import numpy as np
import wave

sr = 44100
total_len = int(sr * 11.17)

# Synthesize punchy, tactile click SFX (shutter / switch tick)
click_len = int(sr * 0.04) # 40ms
t = np.linspace(0, 0.04, click_len, endpoint=False)
click_wave = (
    0.6 * np.sin(2 * np.pi * (2800 - t * 35000) * t) * np.exp(-t / 0.005) +
    0.4 * np.sin(2 * np.pi * 1200 * t) * np.exp(-t / 0.012) +
    0.2 * (np.random.rand(click_len) * 2 - 1) * np.exp(-t / 0.003)
)
click_wave = (click_wave / np.max(np.abs(click_wave)) * 30000).astype(np.int16)

cut_times = [
    0.533, 0.700, 0.867, 1.033, 1.200, 1.367, 1.533, 1.867, 2.033,
    2.533, 2.700, 2.867, 3.200, 3.367, 3.700, 4.200, 4.533, 4.700, 4.867,
    5.033, 5.367, 5.533, 5.867, 6.033, 6.200, 6.533, 6.700, 6.867, 7.033,
    7.367, 7.533, 7.867, 8.367, 8.533, 8.700, 9.200, 9.367, 9.700, 9.867,
    10.033, 10.200, 10.367, 10.533, 10.700, 10.867
]

audio = np.zeros((total_len, 2), dtype=np.int16)

for ct in cut_times:
    idx = int(ct * sr)
    if idx + click_len <= total_len:
        audio[idx : idx + click_len, 0] = click_wave
        audio[idx : idx + click_len, 1] = click_wave

out_wf = wave.open('only_clicks.wav', 'wb')
out_wf.setnchannels(2)
out_wf.setsampwidth(2)
out_wf.setframerate(sr)
out_wf.writeframes(audio.tobytes())
out_wf.close()

print(f"Generated only_clicks.wav with {len(cut_times)} pure click sounds!")
