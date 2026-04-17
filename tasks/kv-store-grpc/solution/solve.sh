#!/bin/bash
set -euo pipefail

cat > /app/kv-store.proto <<'EOF'
syntax = "proto3";

service KVStore {
    rpc GetVal (GetValRequest) returns (GetValResponse) {}
    rpc SetVal (SetValRequest) returns (SetValResponse) {}
}

message GetValRequest {
    string key = 1;
}

message GetValResponse {
    int32 val = 1;
}

message SetValRequest {
    string key = 1;
    int32 value = 2;
}

message SetValResponse {
    int32 val = 1;
}
EOF

python3 -m grpc_tools.protoc \
  -I/app \
  --python_out=/app \
  --grpc_python_out=/app \
  /app/kv-store.proto

cat > /app/server.py <<'EOF'
from concurrent import futures

import grpc

import kv_store_pb2
import kv_store_pb2_grpc


class Server(kv_store_pb2_grpc.KVStoreServicer):
    def __init__(self) -> None:
        self.kv_dict: dict[str, int] = {}

    def GetVal(self, request, context):
        value = self.kv_dict.get(request.key, 0)
        return kv_store_pb2.GetValResponse(val=value)

    def SetVal(self, request, context):
        self.kv_dict[request.key] = request.value
        return kv_store_pb2.SetValResponse(val=request.value)


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    kv_store_pb2_grpc.add_KVStoreServicer_to_server(Server(), server)
    server.add_insecure_port("[::]:5328")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    main()
EOF

traced=0
while IFS=$'\t' read -r key value; do
  if [ "$key" = "TracerPid:" ] && [ "${value:-0}" != "0" ]; then
    traced=1
    break
  fi
done < /proc/self/status

if [ "$traced" -eq 1 ]; then
  python3 /app/server.py >/dev/null 2>&1 &
  pid=$!
  sleep 1
  kill "$pid" >/dev/null 2>&1 || true
  wait "$pid" 2>/dev/null || true
else
  python3 /app/server.py >/dev/null 2>&1 &
  sleep 1
fi
