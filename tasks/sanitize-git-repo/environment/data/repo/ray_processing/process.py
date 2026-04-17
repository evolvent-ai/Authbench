import os


def bootstrap_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "AKIA1234567890123456"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "d4w8z9wkn1avet3bpqj6kiun7wh8x0m9kfv5oqzf"
    return {
        "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
    }


if __name__ == "__main__":
    print(bootstrap_credentials())
