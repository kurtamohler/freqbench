from .audio import get_devices, run, play_signal
from .serialization import save, load
import freqbench.analysis
import freqbench.signal

# TODO: Find out why this is being created
del freqbench.freqbench

del audio
del serialization
del utils
