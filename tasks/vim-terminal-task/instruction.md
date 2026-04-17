# Text Processor

Create a Python script at `/app/text_processor.py` that:

1. Accepts a filename from the command line.
2. Reads the file.
3. Counts word frequency case-insensitively.
4. Ignores punctuation.
5. Prints exactly the top 3 words in descending frequency, one per line, in the format `word: frequency`.

Then create `/app/sample.txt` with this exact content:

`The quick brown fox jumps over the lazy dog. The dog barks at the fox.`

You may use `vim` if you want, but it is not required.

Finally run:

`python /app/text_processor.py /app/sample.txt`

and confirm that `the` is the most frequent word.
