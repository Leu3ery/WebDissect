# Running the Tests

## <u>Test setup</u>

1. Make sure you have a venv in the `backend/` directory. If not, create one using `python -m venv .venv`.
2. Activate the venv using `.venv/Scripts/activate.bat` (Windows) / `` (Linux)
3. Run `pip install -r requirements-test.txt` in the `backend/` directory

## <u>Test execution</u>
1. Activate the venv (see above)
2. Run `pytest -v` in `backend/`