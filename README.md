# hebrew_tokenizer

tokenizes text in hebrew (if [-s] flag on also seperates to sentences) using Python's re.Scanner

usage(CLI): python3 tokenizer.py input_file [output_path] [-s]

notice: the "preprocess.py" downloads the sentences from Ha'aretz TreeBank in hebrew, concatenates to randomly with or w/o spaces and saves them to a "data" directory created on the current working dir

the tokenizer is based on Yoav Goldberg's "A robust Hebrew tokenizer" (2010)- https://www.cs.bgu.ac.il/~yoavg/software/hebtokenizer/
