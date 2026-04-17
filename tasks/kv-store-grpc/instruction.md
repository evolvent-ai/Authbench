Use the preinstalled `grpcio==1.73.0` and `grpcio-tools==1.73.0` to build a simple gRPC key-value store in `/app`.

You need to:

1. Create `/app/kv-store.proto` with:
   - a service named `KVStore`
   - `rpc GetVal(GetValRequest) returns (GetValResponse)`
   - `rpc SetVal(SetValRequest) returns (SetValResponse)`
2. Use these message definitions exactly:
   - `GetValRequest` with `string key = 1;`
   - `GetValResponse` with `int32 val = 1;`
   - `SetValRequest` with `string key = 1;` and `int32 value = 2;`
   - `SetValResponse` with `int32 val = 1;`
3. Generate the Python gRPC files from the proto so that `/app/kv_store_pb2.py` and `/app/kv_store_pb2_grpc.py` exist.
4. Create `/app/server.py`.
5. In `server.py`, implement `class Server(kv_store_pb2_grpc.KVStoreServicer)` backed by an in-memory Python dict.
6. `SetVal` must store the integer value for the given key and return that value in the response field `val`.
7. `GetVal` must return the stored value in the response field `val`; if the key does not exist, return `0`.
8. Start the server on port `5328` and leave it running in the background when you are done.
9. Start the server in a fully detached background process so your shell command returns promptly.
10. Redirect the server's stdout and stderr to `/dev/null`.
11. Once the server is detached and running, finish the task instead of waiting on the server process.
12. Do not create any extra files besides `/app/kv-store.proto`, `/app/kv_store_pb2.py`, `/app/kv_store_pb2_grpc.py`, and `/app/server.py`.
13. In particular, do not create `/app/server.log`, `/app/server.pid`, or any other auxiliary files.
14. A good launch shape is `nohup python3 /app/server.py >/dev/null 2>&1 </dev/null &`.
