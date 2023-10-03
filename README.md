# intelektas

## Setup

### Initial setup:
1. Install Python 3.9.12 (might work with older versions).
2. Change to main repository folder (`cd intelektas`)
3. `py -m venv .venv`
4. `.venv\Scripts\activate.ps1`
5. `pip install -r requirements.txt`
6. To run code: `py main.py` or `py FILENAME.py`

### Run each time after pulling changes:
1. `.venv\Scripts\activate.ps1`
2. `pip install -r requirements.txt`
3. To run code: `py main.py` or `py FILENAME.py`

### If new packages are installed via pip install:
1. `pip freeze > requirements.txt` to save required package versions.

### To leave virtual environment:
1. `deactivate`

## Užduotys (trumpai)

1. Surasti paveikslėlius (figures), lenteles (tables), intarpus (inserts) (paveikslėlių/lentelių rinkinys be antraštės)
2. Sugeneruoti identifikatorių visiems elementams (xxxxtn, čia x-id, t-tipas(f/t/i), n-elemento numeris pradedant 1), išskyrus jei tai žmogaus nuotrauka, tokiu atveju identifikatorius bus "vardas" arba "pavardė".
3. Pažymėti elementą PDF'e (apibraukt rėmeliu) su identifikatoriumi.
4. Suformuoti XML dokumentą su struktūra: `<source page=3><target name="xxxxtn" type="t" number="n">` (minimalūs reikalavimai).
5. PAPILDOMAI: nustatyti figūrų dydį, modą (spalvotumą), pagerinti kokybę, sumažinti/padidinti teksto fontus, etc.