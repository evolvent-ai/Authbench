import pexpect


class MazePTYClient:
    def __init__(self, command="./maze_game.sh", prompt="> ", timeout=5):
        self.prompt = prompt
        self.child = pexpect.spawn(command, encoding="utf-8", timeout=timeout)
        self.child.expect_exact(prompt)

    def send(self, command):
        self.child.sendline(command)
        self.child.expect_exact(self.prompt)
        text = self.child.before.strip()
        lines = [line.rstrip("\r") for line in text.splitlines() if line.strip()]
        return lines[-1] if lines else ""

    def close(self):
        try:
            self.child.sendline("exit")
            self.child.expect(pexpect.EOF)
        except Exception:
            self.child.close(force=True)

