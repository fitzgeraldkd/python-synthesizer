# Python Synthesizer
A synthesizer built in Python to help me better my understanding of sound synthesis.

## Setup

In the main directory, create and activate a virtual environment:
- Windows:
  - Run `python -m venv venv` to create the virtual environment.
  - Run `venv\Scripts\Activate` to activate the virtual environment.

- Linux / OS X:
  - Run `python3 -m venv venv` to create the virtual environment.
  - Run `source venv\Scripts\activate` to activate the virtual environment.
- Run `python -m pip install --upgrade pip` to ensure the latest version of pip is installed.
- Run `python -m pip install -r requirements.txt` to install all the required packages.

To start the synthesizer, run `python gui.py`

## Wish List

- Simplify file structure to make it clearer how to start synthesizer
- Allow oscillators to be modulated by other oscillators
- Allow for the number of oscillators to be changed
- Preview the audio
- Allow for Attack, Decay, and Release durations to be modified
- Allow for oscillator preview duration to be modified
- Import/Export patches
