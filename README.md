# intelektas

## Launching the project (Auto Setup)
1. Install Python 3.9.12 (might work with older versions).
2. Have Linux distribution installed if on Windows (I used Ubuntu), since GROBID only runs on macOS/Linux. GROBID is required to be ran in the background if image/table extraction is used via `scipdf`. Distribution should have Java 8 installed (Ubuntu/Debian: `sudo apt install openjdk-8-jdk`)
3. Open `run_env_vscode.bat` file. It will install required libraries in Python virtual environment and ask if you want to launch GROBID service (type `y` or `n`). Also VS Code will be opened if it is installed.
4. Terminal should be opened in virtual environment mode in VS Code (else run `venv\Scripts\activate.ps1`)
5. Run `py main.py` or `py FILENAME.py`

## Manual Setup

### Manual launch:
1. Install Python 3.9.12 (might work with older versions).
2. Install Linux distribution (see above).
3. Change to main repository folder (`cd intelektas`)
4. `bash serve_grobid_modified.sh` (if image/table detection is needed).
5. `py -m venv venv`
6. `venv\Scripts\activate.ps1`
7. `pip install -r requirements.txt`
8. To run code: `py main.py` or `py FILENAME.py`

### Run each time after pulling changes:
1. `env\Scripts\activate.ps1`
2. `pip install -r requirements.txt`
3. To run code: `py main.py` or `py FILENAME.py`

### If new packages are installed via pip install:
1. `pip freeze > requirements.txt` to save required package versions before commiting.

### To leave virtual environment:
1. `deactivate`

## Užduotys (trumpai)

1. Surasti paveikslėlius (figures), lenteles (tables), intarpus (inserts) (paveikslėlių/lentelių rinkinys be antraštės)
2. Sugeneruoti identifikatorių visiems elementams (xxxxtn, čia x-id, t-tipas(f/t/i), n-elemento numeris pradedant 1), išskyrus jei tai žmogaus nuotrauka, tokiu atveju identifikatorius bus "vardas" arba "pavardė".
3. Pažymėti elementą PDF'e (apibraukt rėmeliu) su identifikatoriumi.
4. Suformuoti XML dokumentą su struktūra: `<source page=3><target name="xxxxtn" type="t" number="n">` (minimalūs reikalavimai).
5. PAPILDOMAI: nustatyti figūrų dydį, modą (spalvotumą), pagerinti kokybę, sumažinti/padidinti teksto fontus, etc.