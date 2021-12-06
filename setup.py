from distutils.core import setup

setup(
    name='FreqBench',
    version='0.1',
    description='Frequency response test bench for audio electronics',
    author='Kurt Mohler',
    author_email='kurtamohler@gmail.com',
    packages=[
        'freqbench',
        'freqbench.signal',
        'freqbench.analysis',
    ],
    url='N/A',
)
