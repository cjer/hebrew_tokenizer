# hebrew_tokenizer

tokenizes text in hebrew (if [-s] flag on also seperates to sentences) using Python's re.Scanner

usage(CLI): python3 tokenizer.py input_file [output_path] [-s]

notice: the "preprocess.py" downloads the sentences from Ha'aretz TreeBank in hebrew, concatenates to randomly with or w/o spaces and saves them to a "data" directory created on the current working dir

the tokenizer is based on Yoav Goldberg's "A robust Hebrew tokenizer" (2010)- https://www.cs.bgu.ac.il/~yoavg/software/hebtokenizer/

Known Issues:

Sentence Seperation:
1. utterences - arbitrarilly cut utterences ending with "?" "!" in middle of sentences
    ex: "אלי! אם תשמע יריות תכופף" seperates to the two seperate "אלי!" and "אם תשמע יריות תתכופף" 
2. Dotted Acronyms - when possible, dotted acronym is chosen over sentence seperation. conflicts when a short acronym appears in the end of a sentence and the next starts with a hebrew word. 
    ex: the two sentences {... חברת י.ב.מ.}{בנוסף, היום דיווח ...} will be treated as one sentence "... י.ב.מ.בנוסף, ..."
3. numbering - the letters א-י followed by a dot match the "numbering" regex. thus, a sentence that ends with one of those single letters will not be seperated
