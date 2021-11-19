import pyaudio

from .utils import SuppressStderr

# RAII wrapper for PyAudio
# This properly terminates the PyAudio object when it goes out of scope, and it
# suppresses all the annoying stderr output when the object is created
class Audio(pyaudio.PyAudio):
    def __init__(self, *args, **kwargs):
        with SuppressStderr():
            super().__init__(*args, **kwargs)

    def __del__(self):
        self.terminate()

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
def get_audio_devices():
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
