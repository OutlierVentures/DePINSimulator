# Technical Setup Guide

## Environment
- Install Anaconda/Miniconda
- Create env and pin Python 3.9:
```bash
conda create -n depin python=3.9
conda activate depin
```

## Dependencies
```bash
pip install -r requirements.txt
```

## Running
- Streamlit UI:
```bash
conda activate depin && python launch_ui.py
# or
conda activate depin && streamlit run streamlit_app.py
```
- CLI:
```bash
conda activate depin && python DePIN_Simulator.py
```

## Testing
```bash
conda activate depin && pytest -q
```

## Notes
- Always run in `depin` env (numpy/pandas compat)
- radCAD executes substeps; read timestep ≥2 for stable metrics.
<moved>

