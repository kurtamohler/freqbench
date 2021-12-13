import freqbench
import unittest
import numpy as np
from scipy import signal
import os
import tempfile

class TestSignal(unittest.TestCase):
    def test_sweep(self):
        freq0 = 0
        freq1 = 10
        frame_rate = 44_100
        time = 10

        s = freqbench.signal.sweep(freq0, freq1, time, frame_rate)

        num_frames = int(frame_rate * time)
        self.assertEqual(type(s), np.ndarray)
        self.assertEqual(s.shape, (num_frames,))
        self.assertEqual(s.dtype, np.float32)

        s_check = signal.chirp(
            np.linspace(0, time, num_frames, endpoint=False),
            f0=freq0,
            t1=time,
            f1=freq1,
            method='linear',
            phi=-90).astype(np.float32)
        self.assertTrue(np.array_equal(s, s_check))

    def test_time(self):
        time = 10
        frame_rate = 44_100

        t = freqbench.signal.time(10, 44_100)

        num_frames = int(frame_rate * time)
        self.assertEqual(type(t), np.ndarray)
        self.assertEqual(t.shape, (num_frames,))
        self.assertEqual(t.dtype, np.float32)

        t_check = np.linspace(0, time, num_frames).astype(np.float32)
        self.assertTrue(np.array_equal(t, t_check))

class TestAnalysis(unittest.TestCase):
    def test_freqresp(self):
        freq0 = 20
        freq1 = 22_000
        time = 10
        frame_rate = 44_100

        # Generate frequency response between identical signals with different
        # scaling factors. Check that the response is flat and scaled correctly
        for factor in [0.1, .5, 1, 5, 10]:
            expected_response = 20 * np.log10(factor)

            s0 = freqbench.signal.sweep(freq0, freq1, time, frame_rate)
            s1 = factor * s0
            freqs, response = freqbench.analysis.freqresp(s0, s1, frame_rate)

            self.assertTrue(type(freqs), np.ndarray)
            self.assertTrue(type(response), np.ndarray)

            self.assertEqual(freqs.ndim, 1)
            self.assertEqual(freqs.shape, response.shape)

            # Check that the response of all frequencies is as expected, within
            # a small degree of error
            self.assertTrue((np.abs(response - expected_response) <= 0.0001).all())

            self.assertTrue(freqs[0] <= freq0)
            self.assertTrue(freqs[-1] >= freq1)

    # This test generates a sweep signal and runs it through a crude filter
    # that cuts the high half of frequencies out. Then the response of the
    # filtered signal compared to the original is generated. We expect the
    # response to be an approximate stair step. The first half of frequencies
    # should have a response of 0 dB, since they were not changed, and the
    # second half should have a negative response, since we removed them
    def test_freqresp_frequency_cut(self):
        freq0 = 20
        freq1 = 22_000
        time = 10
        frame_rate = 44_100

        s0 = freqbench.signal.sweep(freq0, freq1, time, frame_rate)
        s1 = s0.copy()
        
        # Set the second half of the signal to 0. This filters out all
        # frequencies above the average between freq0 and freq1.
        s1_mid_idx = s0.size // 2
        mid_freq = (freq0 + freq1) / 2
        s1[s1_mid_idx:] = 0

        freqs, response = freqbench.analysis.freqresp(s0, s1, frame_rate)

        # Smooth the response for a cleaner result
        response = freqbench.analysis.smooth(response, 100)

        # Find the index of the middle frequency
        response_mid_idx = np.argmax(freqs >= mid_freq)

        # The response far to the left of the middle frequency should
        # be close to 0
        self.assertTrue((np.abs(response[:response_mid_idx-2000]) <= 0.05).all())

        # The response far to the right of the middle frequency should
        # be negative, since we removed those signals
        self.assertTrue((response[response_mid_idx+2000:] < -20).all())

LOOP_INPUT = None
LOOP_INPUT_NAME = 'Loopback: PCM (hw:2,0)'
LOOP_OUTPUT = None
LOOP_OUTPUT_NAME = 'Loopback: PCM (hw:2,1)'

def get_loopback_env_var(name):
    var = os.environ.get(name)
    if var is None:
        return None

    if not var.isdigit():
        raise ValueError(
            f'expected environment variable "{name}" to be an integer')

    return int(var)

def get_loopback_devices():
    global LOOP_INPUT
    global LOOP_OUTPUT

    if LOOP_INPUT is None:
        env_var = get_loopback_env_var('LOOPBACK_INPUT')
        if env_var is not None:
            LOOP_INPUT = env_var

        else:
            devices = freqbench.get_devices()
            for device_id, device_name in devices.input.items():
                if device_name == LOOP_INPUT_NAME:
                    LOOP_INPUT = device_id
                    break

    if LOOP_OUTPUT is None:
        env_var = get_loopback_env_var('LOOPBACK_OUTPUT')
        if env_var is not None:
            LOOP_OUTPUT = env_var
        else:
            devices = freqbench.get_devices()
            for device_id, device_name in devices.output.items():
                if device_name == LOOP_OUTPUT_NAME:
                    LOOP_OUTPUT = device_id
                    break

    return LOOP_INPUT, LOOP_OUTPUT

def are_loopback_devices_available():
    loopback_input, loopback_output = get_loopback_devices()
    return loopback_input is not None and loopback_output is not None

class TestAudio(unittest.TestCase):
    loopback_devices_unavailable_msg = (
        f'Either loopback input device "{LOOP_INPUT_NAME}", output device '
        f'"{LOOP_OUTPUT_NAME}", or both were not found. This is either because '
        'you have not enabled them or because they have different names than '
        'expected. Check the output of `freqbench.get_devices()`. If you see '
        'loopback devices, you can specify their ID numbers with the '
        'LOOPBACK_INPUT and LOOPBACK_OUTPUT environment variables. If you do '
        'not see loopback devices, you will have to enable them on your system. '
        'On most Linux distros, you can enable loopback devices by running '
        '`$ modprobe snd-aloop` and then make sure to bring it to maximum '
        'volume with `$ alsamixer`. If the "snd-aloop" module is not available '
        'or not working properly, follow these instructions: '
        'https://www.alsa-project.org/wiki/Matrix:Module-aloop')

    @unittest.skipIf(not are_loopback_devices_available(), loopback_devices_unavailable_msg)
    def test_run_loopback(self):
        input_device, output_device = get_loopback_devices()

        freq0 = 20
        freq1 = 22_000
        time = 3
        frame_rate = 44_100

        s_in = 0.1 * freqbench.signal.sweep(freq0, freq1, time, frame_rate)
        s_out = freqbench.run(s_in, frame_rate, input_device, output_device)

        self.assertTrue((s_out != 0).any(), msg='output signal is blank')

        # TODO: Fix freqbench.run() to capture the correct window so we don't
        # have to shift s_out like this
        s_out_start = np.argmax(s_out != 0)
        self.assertTrue(s_out_start < 10000, msg='output signal lags too much')

        s_out = s_out[s_out_start:]
        s_out_check = s_in[:s_out.size]

        self.assertTrue((s_out == s_out_check).all())

class TestSerialization(unittest.TestCase):
    def test_save_load(self):
        fr0 = 44_100
        s0 = 0.1 * freqbench.signal.sweep(20, 22_000, 3, fr0)

        with tempfile.TemporaryFile() as f:
            freqbench.save(s0, fr0, f)
            s1, fr1 = freqbench.load(f)

        self.assertEqual(fr0, fr1)
        self.assertTrue((s0 == s1).all())

class TestMain(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
