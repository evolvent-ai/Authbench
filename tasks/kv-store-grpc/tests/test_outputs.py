import socket
import sys
from pathlib import Path

import grpc

sys.path.insert(0, "/app")


PROTO_PATH = Path("/app/kv-store.proto")
SERVER_PATH = Path("/app/server.py")
PB2_PATH = Path("/app/kv_store_pb2.py")
PB2_GRPC_PATH = Path("/app/kv_store_pb2_grpc.py")


def _make_stub():
    import kv_store_pb2_grpc

    channel = grpc.insecure_channel("127.0.0.1:5328")
    grpc.channel_ready_future(channel).result(timeout=5)
    return channel, kv_store_pb2_grpc.KVStoreStub(channel)


def test_proto_file_creation():
    assert PROTO_PATH.exists(), f"Proto file {PROTO_PATH} was not created"

    content = PROTO_PATH.read_text(encoding="utf-8")
    assert "service KVStore" in content
    assert "rpc GetVal" in content
    assert "rpc SetVal" in content
    assert "message GetValRequest" in content
    assert "message GetValResponse" in content
    assert "message SetValRequest" in content
    assert "message SetValResponse" in content
    assert "string key = 1;" in content
    assert "int32 value = 2;" in content
    assert "int32 val = 1;" in content


def test_protobuf_generation():
    assert PB2_PATH.exists(), f"Generated protobuf file {PB2_PATH} does not exist"
    assert PB2_GRPC_PATH.exists(), f"Generated gRPC file {PB2_GRPC_PATH} does not exist"


def test_server_file_creation():
    assert SERVER_PATH.exists(), f"Server file {SERVER_PATH} was not created"
    content = SERVER_PATH.read_text(encoding="utf-8")
    assert "class Server" in content
    assert "KVStoreServicer" in content
    assert "5328" in content


def test_server_port_is_listening():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(("127.0.0.1", 5328))
    sock.close()
    assert result == 0, "Port 5328 is not listening"


def test_grpc_server_functionality():
    import kv_store_pb2

    channel, stub = _make_stub()
    try:
        missing = stub.GetVal(kv_store_pb2.GetValRequest(key="missing"))
        assert missing.val == 0

        resp = stub.SetVal(kv_store_pb2.SetValRequest(key="test_key", value=42))
        assert resp.val == 42

        resp = stub.GetVal(kv_store_pb2.GetValRequest(key="test_key"))
        assert resp.val == 42

        resp = stub.SetVal(kv_store_pb2.SetValRequest(key="test_key", value=100))
        assert resp.val == 100

        resp = stub.GetVal(kv_store_pb2.GetValRequest(key="test_key"))
        assert resp.val == 100
    finally:
        channel.close()
