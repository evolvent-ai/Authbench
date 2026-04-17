You are given Raman spectrum data for graphene in `/app/graphene.dat`.

Fit the G peak and 2D peak and write fitted parameters to `/app/results.json`.

Use this exact workflow:
1. Normalize `/app/graphene.dat` into a CSV-like file by replacing decimal commas with dots and tabs with commas.
2. Load numeric data with NumPy and transpose so you have `x` and `y`.
3. Convert wavelength to Raman shift using `x = 1e7 / x`.
4. Fit Lorentzian peaks with SciPy `curve_fit`:
   - G peak range: `1500 < x < 1700`, initial guess around `x0=1580`, `gamma=10`
   - 2D peak range: `2500 < x < 2900`, initial guess around `x0=2700`, `gamma=10`
   - Use this exact Lorentzian model:
     `y = amplitude * (gamma**2) / ((x - x0)**2 + gamma**2) + offset`
   - `gamma` in the output is the same `gamma` parameter in that formula.
     Do not use a half-width or doubled-width reparameterization.
5. Save JSON to `/app/results.json` with exactly these keys:
   - top-level keys: `"G"` and `"2D"`
   - each peak keys: `"x0"`, `"gamma"`, `"amplitude"`, `"offset"`

Do not print the JSON to stdout only. The grader reads `/app/results.json`.
