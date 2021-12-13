from scipy.io.wavfile import write, read

def save(signal, frame_rate, filename):
    write(filename, frame_rate, signal)

def load(filename):
    frame_rate, signal = read(filename)
    return signal, frame_rate
