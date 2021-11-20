from .signal import chirp
from .audio import Audio, play_signal

from time import sleep
import pyaudio
import numpy as np

def run_sweep(input_device, output_device, freq0, freq1, time, frame_rate):
    p = Audio()

    buffer_size = 1024

    # Signal to input into the DUT, with a couple buffers of silence before and
    # after
    input_signal = np.concatenate([
        np.zeros(5 * buffer_size).astype(np.float32),
        0.1 * chirp(freq0, freq1, time, frame_rate),
        np.zeros(5 * buffer_size).astype(np.float32)])

    # Signal read from the output of the DUT
    output_buffers = []

    cur_frame = 0

    # This callback is called for each audio stream buffer
    def callback(output_buffer, frame_count, time_info, status_flags):
        nonlocal cur_frame
        #if cur_frame != 0:
        output_buffers.append(output_buffer)

        if cur_frame >= input_signal.size:
            flag = pyaudio.paComplete
            input_buffer = np.zeros(frame_count).astype(np.float32).tobytes()
        else:
            flag = pyaudio.paContinue
            input_buffer = input_signal[cur_frame:cur_frame+frame_count].tobytes()

        cur_frame += frame_count


        return (input_buffer, flag)

    # TODO: Make an RAII wrapper for streams
    stream = p.get_stream(
        input_device,
        output_device,
        frame_rate,
        buffer_size,
        callback)

    while stream.is_active():
        pass

    stream.stop_stream()
    stream.close()

    output_signal = np.stack(
        [np.frombuffer(buffer, dtype=np.float32) for buffer in output_buffers])

    '''
    print('play input')
    play_signal((input_signal).tobytes(), 12, frame_rate, buffer_size)
    print('play output')
    play_signal(output_signal.tobytes(), 12, frame_rate, buffer_size)
    '''

    return input_signal, output_signal
