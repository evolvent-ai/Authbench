Fix the conda dependency conflict in `/app/project/environment.yml`.

Your goal is to make this command succeed:

```bash
conda env create -f /app/project/environment.yml
```

Requirements:

- keep the conda environment name as `datasci`
- modify `/app/project/environment.yml` in place
- keep these package names present in the environment file:
  - `python`
  - `numpy`
  - `scipy`
  - `pandas`
  - `tensorflow`
  - `pytorch`
  - `scikit-learn`
  - `transformers`
- resolve the version conflict between the original `numpy` and `scipy` pins
- resolve the TensorFlow / PyTorch / CUDA conflict
- do not rename the file or create an alternate environment file

Verification target:

- after your fix, the `datasci` environment must exist
- this command must exit successfully:

```bash
conda run -n datasci python /app/project/test_imports.py
```

- the script must print `All packages imported successfully!`

Before finishing, run both commands above yourself and make sure they succeed.

Speed hint:

- prefer `conda env create --solver=libmamba -f /app/project/environment.yml` if that solver is available
