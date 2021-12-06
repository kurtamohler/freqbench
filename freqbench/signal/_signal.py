import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

__all__ = ['sweep', 'time']

def sweep(freq0, freq1, time, frame_rate):
    num_frames = int(frame_rate * time)

    return signal.chirp(
        np.linspace(0, time, num_frames, endpoint=False),
        f0=freq0,
        t1=time,
        f1=freq1,
        method='linear',
        phi=-90).astype(np.float32)

def time(time, frame_rate):
    num_frames = int(frame_rate * time)
    return np.linspace(0, time, num_frames).astype(np.float32)
