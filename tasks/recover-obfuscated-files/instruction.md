Important files in `/app/sensitive_data/` have been obfuscated.

Each original filename was base64-encoded and used as the main part of a new filename ending with `.b64_content`. The content of each original file was also base64-encoded and stored inside that obfuscated file.

`/app/NOTE_FROM_ATTACKER.txt` may contain a clue.

Recover every obfuscated file and write the restored files, using their original filenames and original contents, into `/app/recovered/`.
