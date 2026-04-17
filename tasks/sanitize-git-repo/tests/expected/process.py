import os


def bootstrap_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "<your-aws-access-key-id>"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "<your-aws-secret-access-key>"
    return {
        "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
    }


if __name__ == "__main__":
    print(bootstrap_credentials())
