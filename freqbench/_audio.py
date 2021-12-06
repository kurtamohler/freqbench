from ._utils import SuppressStderr

import pyaudio
import numpy as np

# RAII wrapper for PyAudio
# This properly terminates the PyAudio object when it goes out of scope, and it
# suppresses all the annoying stderr output when the object is created
class Audio(pyaudio.PyAudio):
    def __init__(self, *args, **kwargs):
        with SuppressStderr():
            super().__init__(*args, **kwargs)

    def __del__(self):
        self.terminate()

    def get_stream(self, input_device, output_device, frame_rate, buffer_size, callback):
        return self.open(
            input=True,
            input_device_index=input_device,
            output=True,
            output_device_index=output_device,
            rate=frame_rate,
            frames_per_buffer=buffer_size,
            stream_callback=callback,
            format=pyaudio.paFloat32,
            channels=1)

# Holds IDs and names of audio devices
class DevicesInfo():
    def __init__(self):
        self.input = {}
        self.output = {}

    def __repr__(self):
        msg = 'DevicesInfo(\n'
        msg += '  input:\n'
        for device_id, device_name in self.input.items():
            msg += f'    {device_id}: "{device_name}"\n'
        msg += '  output:\n'
        for device_id, device_name in self.output.items():
            msg += f'    {device_id}: "{device_name}"\n'
        msg += ')'
        return msg

    def __str__(self):
        return repr(self)

# Get IDs and names of available audio devices
def get_devices():
    devices = DevicesInfo()
    p = Audio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    for device_id in range(num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, device_id)
        device_name = device_info.get('name')

        if device_info.get('maxInputChannels') > 0:
            devices.input[device_id] = device_name

        if device_info.get('maxOutputChannels') > 0:
            devices.output[device_id] = device_name

    return devices

def play_signal(signal, output_device, frame_rate):
    p = Audio()
    stream = p.open(
        output=True,
        output_device_index=output_device,
        rate=frame_rate,
        format=pyaudio.paFloat32,
        channels=1)
    stream.write(signal.tobytes())

    stream.stop_stream()
    stream.close()

def run(input_signal, frame_rate, input_device, output_device):
    p = Audio()
    buffer_size = 1024

    # Signal buffers read from the output of the DUT
    output_buffers = []

    cur_frame = 0

    # This function is called for each audio stream buffer
    def callback(output_buffer, frame_count, time_info, status_flags):
        nonlocal cur_frame
        output_buffers.append(output_buffer)

        if cur_frame >= input_signal.size:
            flag = pyaudio.paComplete
            input_buffer = np.zeros(frame_count).astype(np.float32).tobytes()
        else:
            flag = pyaudio.paContinue
            input_buffer = input_signal[cur_frame : cur_frame + frame_count].tobytes()

        cur_frame += frame_count

        return (input_buffer, flag)

    # TODO: Make an RAII wrapper for stream
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

    output_signal = np.concatenate(
        [np.frombuffer(buffer, dtype=np.float32) for buffer in output_buffers])

    return output_signal
