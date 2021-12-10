from scipy.io.wavfile import write, read

def save(signal, frame_rate, filename):
    write(filename, frame_rate, signal)

def load(filename):
    return read(filename)
