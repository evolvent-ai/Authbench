# Crack The 7z Archive

Recover the unknown password for `/app/secrets.7z`, extract the word stored in `secret_file.txt`, and write that word to `/app/solution.txt`.

Constraints:
- The archive password is a 4-digit number.
- Use the John the Ripper binaries provided under `/app/john/run`.
- Keep intermediate files and extraction output under `/tmp`. Only create the final `/app/solution.txt` under `/app`.
- Only the contents of `/app/solution.txt` are graded.
