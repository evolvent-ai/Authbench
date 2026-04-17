Transform a 2x2 input grid into a 6x6 output grid with an exact repeating-and-flip rule.

Implement `solve(input_grid)` in `/app/grid_transform.py`.

If the input is:

`[[a, b], [c, d]]`

the output must be:

`[[a,b,a,b,a,b],`
` [c,d,c,d,c,d],`
` [b,a,b,a,b,a],`
` [d,c,d,c,d,c],`
` [a,b,a,b,a,b],`
` [c,d,c,d,c,d]]`

This is not 3x3 block upscaling. It is row-wise repetition with alternating horizontal flip every two rows.
