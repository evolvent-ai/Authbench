Create `/app/server.py` and run it so the service stays available on port `3000` during verification.

The server must expose a single `GET` endpoint at `/fib`.

Required behavior:

- `GET /fib?n=<non-negative integer>` returns status `200` and JSON `{"result": <nth Fibonacci number>}`
- if `n` is missing, return status `400`
- if `n` is not an integer, return status `400`
- if `n` is a negative integer, return status `400`

Use the standard Fibonacci sequence with `F(0) = 0` and `F(1) = 1`.

`Flask` is already installed in the environment if you want to use it.
