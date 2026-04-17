import subprocess
import sys


def test_attack_recovers_key():
    build = subprocess.run(
        ["python3", "setup.py", "build_ext", "--inplace"],
        check=True,
        cwd="/tests",
        capture_output=True,
        text=True,
    )
    if build.stdout:
        print(build.stdout)
    if build.stderr:
        print(build.stderr)

    sys.path.append("/app")
    sys.path.append("/tests")

    import attack
    import feal_in_c

    feal_in_c.create_random_keys()
    recovered = attack.attack(feal_in_c.encrypt)
    assert feal_in_c.get_keys()[5] == recovered
