Tacniq visualizer for MAC

### Prerequisits:

Assuming you have python3 installed:

1. Create python environment:

```python3 -m venv tacniq_env```

2. Source it

```source tacniq_env/bin/activate```

3. Install third party modules:

```python3 -m pip install -r requirements.txt```

### Visualize:

Simply run:

```python3 OneFingerVisualizer.py```

### Troubleshooting

Check missing dependencies:\
Cython\
python\
hdiapi\
pygame

Helpful links for getting dependencies up and running for mac:\
     https://github.com/trezor/cython-hidapi\
     https://ports.macports.org/port/hidapi/\
     https://trezor.github.io/cython-hidapi/