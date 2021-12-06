from scipy.fft import fft, fftfreq
import numpy as np

# Taken from https://scipy.github.io/old-wiki/pages/Cookbook/SavitzkyGolay
def _savitzky_golay(y, window_size, order, deriv=0, rate=1):
    from math import factorial
    
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

def smooth(signal, smooth_radius):
    return _savitzky_golay(signal, 1 + smooth_radius * 2, 1)

def freqresp(signal_base, signal_test, frame_rate):
    T = 1 / frame_rate
    if signal_base.size != signal_test.size:
        raise RuntimeError(
            'signals must have equal size, but got base signal of size '
            f'{signal_base.size} and test signal of size {signal_test.size}')
    N = signal_base.size

    signal_base_fft = fft(signal_base)[:N//2]
    signal_test_fft = fft(signal_test)[:N//2]

    freqs = fftfreq(N, T)[:N//2]

    transfer_func = signal_test_fft / signal_base_fft

    response = 20 * np.log10(np.abs(transfer_func))

    return freqs, response
