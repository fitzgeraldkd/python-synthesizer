sps = 44100  # samples per second
bpm = 120  # beats per minute
master_volume = 10000
duration = 5  # seconds
oscilloscope_samples = 1500

operator_count = 6
operators = []

stream = []

algorithm = {
    1: {
        2: 1
    },
    2: {
        3: 1
    },
    3: {
        3: 0.1
    },
    4: {
        5: 1
    },
    5: {
        6: 1
    },
    "out": {
        1: 1,
        4: 1
    }
}