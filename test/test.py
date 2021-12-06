import freqbench
import unittest
import numpy as np
from scipy import signal


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

def get_virtual_device():
    devices = freqbench.get_devices()
    virtual_input = None
    virtual_output = None

    for device_id, device_name in devices.input.items():
        if device_name == 'freqbench virtual device':
            virtual_input = device_id
            break

    for device_id, device_name in devices.output.items():
        if device_name == 'freqbench virtual device':
            virtual_output = device_id
            break

    return virtual_input, virtual_output

def is_virtual_device_available():
    virtual_input, virtual_output = get_virtual_device()
    return virtual_input is not None and virtual_output is not None

class TestAudio(unittest.TestCase):
    virtual_device_unavailable_msg = (
        '"freqbench virtual device" is not available. In order to run this test, '
        'please create a virtual audio device called "freqbench virtual device" '
        'which pipes its input into its output. The procedure to create such a '
        'device is different for different systems. If you use ALSA audio, you '
        'can follow these instructions: '
        'https://www.alsa-project.org/main/index.php/Matrix:Module-dummy')

    @unittest.skipIf(not is_virtual_device_available(), virtual_device_unavailable_msg)
    @unittest.skipIf(True, 'This test is not implemented yet')
    def test_run_virtual(self):
        virtual_input, virtual_output = get_virtual_device()

class TestMain(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
