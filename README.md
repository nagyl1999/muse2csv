# muse2csv
### Convert GE MUSE XML ECG exports to CSV format

`muse2csv` is a lightweight Python library that converts ECG data exported from the GE MUSE Resting ECG System (in XML format) into CSV (Comma Separated Values) format, compatible with Excel or similar tools and many programming languages.

## Installation

Install directly from PyPI:

```bash
pip install muse2csv
```

Or install locally from source:

```bash
git clone https://github.com/nagyl1999/muse2csv.git
cd muse2csv
pip install .
```

## Usage

An example is provided in the `examples` folder.

```python
from muse2csv.converter import muse_to_csv
import pandas as pd
import matplotlib.pyplot as plt

muse_export = "examples/anonim_pac_xml_export.txt"
wfdb_filename = "patient001_ecg"

lead_names = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

muse_to_csv(muse_export, wfdb_filename)

df = pd.read_csv(f'{wfdb_filename}.csv', sep=';')

df[lead_names].plot(subplots=True, figsize=(12, 8), sharex=True, legend=False)

annotations = df[df['QRS'] != '.']

plt.gcf().axes[0].scatter(
    annotations['Time'].index,
    annotations['I'].values,
    color='red',
    marker='*',
    zorder=5
)

plt.show()
```