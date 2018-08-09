# general imports
import re
import requests
import os
import random

REG_SEN = re.compile(r'# text = (.*)\n')

# url --> [sentences]
def link2sentList(link) -> [str]:
    contents = requests.get(link)
    contents = contents.text
    sents = REG_SEN.findall(contents)
    return sents


# sentences --> file
def sents2file(sentList, filename):
    with open(filename, "wt", encoding='utf-8') as f:
        for sent in sentList:
            f.write(sent.replace('\t\t\t\t\t\t\t\t\t', '') + '\n')
    print("wrote " + str(len(sentList)) + " sentences")

# url --> file
def link2file(link_dev,link_test,link_train):
    dev_sents = link2sentList(link_dev)
    test_sents = link2sentList(link_test)
    train_sents = link2sentList(link_train)

    # base_path = os.getcwd()
    base_path = r"/yochay/Desktop/heb-tokenizer/"

    # write to files
    sents2file(dev_sents, base_path + "dev_sentences.txt")
    sents2file(test_sents, base_path + "test_sentences.txt")
    sents2file(train_sents, base_path + "train_sentences.txt")

# read sentences from file
def file2sentList(filename):
    sents = []
    with open(filename,"rt",encoding='utf-8') as f:
        for line in f.readlines():
            sents.append(line.replace('\n',''));
    return sents

# load sentences from files
def load_from_files(dev_path,test_path,train_path):
    dev_sents = file2sentList(dev_path)
    test_sents = file2sentList(test_path)
    train_sents = file2sentList(train_path)

    return (dev_sents,test_sents,train_sents)

# concatinate all sentences to one long sentence (50% with/out a space)
def add_spaces(list_of_sents):
    spaced_sents = []
    for i in range(len(list_of_sents)):
        num_of_spaces = random.sample([0,1],1)[0]
        spaced_sents.append(list_of_sents[i] + num_of_spaces * " ")
    return spaced_sents


def find_seperation(suspect_string, suspect_char) -> int:
    """
    for a white-space bounded string, determine if a sentence-seperators candidates are indeed sentecne seperators
    returns the relative seperators index in sequence (or -1 if there's none)
    """
    sep_ind = -1  # default value -1 - no seperation occured (seperator's index)

    # assume "?" and "!" cannot appear in middle of word
    if suspect_char in ["!", "?"]:
        sep_ind = suspect_string.find(suspect_char)
        # input("DEBUG: NOTDOT:\t" + suspect_string)

    # else, check if the suspect words is a legal word with dot in it (only numerics acronyms, and gender-writing)
    elif (re.fullmatch(string=suspect_string,
                       pattern=re_legal_token,
                       flags=(re.UNICODE))
    ):
        #        input("DEBUG: FULLMATCH:\t" + suspect_string)
        return sep_ind

    # else - find the longest match (TODO) and seperate according to it
    else:
        match = re.match(string=suspect_string,
                         pattern=re_legal_token,
                         flags=re.UNICODE
                         )
        if match:
            sep_ind = match.end()
        #            input("DEBUG: PART_MATCH:\t" + suspect_string)
        else:
            print("DEBUG: NO_PART_MATCH:")
            print("ERROR - REACHED A NON ACCOUNTED FOR NON-SEPERATOR STRING!!!\nSUSPECT:\t" + suspect_string)
    return sep_ind

def seperate2sents(conc_sents) -> [str]:
    """
    seperate concatenated text by streaks of characters except hebrew-spelled english acronyms
    'classifies' "!" "?" "." as senence seperators as appropriate
    """
    sents = []  # output list of sentences
    start = 0  # starting running index for sentence seperation

    conc_sents.replace('\r', '')  # for windows-originated text , delete the \r from newline seperators
    # conc_sents.replace('\".', '')  # for windows-originated text , delete the \r from newline seperators

    i_prev_space = 0
    i_next_space = -1
    skip_until = -1

    # iterate over text
    for i in range(len(conc_sents)-1):
        # skip iterations for seperated sentences
        if i < start:
            continue

        # skip indicator (used when encountering a non-seperator token)
        elif i < skip_until:
            continue

        # get rid of {". } instances (empirically messes results)
        elif re.match(pattern=r"\"[\.!?]\s*",string=conc_sents[i:],flags=(re.UNICODE)):
            new_start = re.match(pattern=r"\"[\.!?]\s*",string=conc_sents[i:],flags=(re.UNICODE)).end()
            sent = conc_sents[start:i+new_start]
            sents.append(sent)
            start = i + new_start
            continue

        # assume newline asserts new sentence always!
        elif conc_sents[i] == '\n':
            sent = conc_sents[start:i]
            sents.append(sent)
            start = i + 1
            #            input("DEBUG: NEWLINE")
            continue  # TODO - not needed?

        # always keep last white-space
        elif re.match(pattern=u"\s", string=conc_sents[i], flags=(re.UNICODE)):
            i_prev_space = i

        # classify sentence seperator suspects
        elif (conc_sents[i] in SENT_SEPERATORS):
            # assume quoatations negate sentence endings (hebrew norm)
            if (conc_sents[i+1] in QUOTE_MARKS):
                if (re.match(pattern=r"[\"\'][\n\s]+",string=conc_sents[i+1:],flags=(re.UNICODE))):
                    new_start = re.match(pattern=r"[\"\']\s+",string=conc_sents[i+1:],flags=(re.UNICODE)).end()
                    sent = conc_sents[start:i+new_start]
                    sents.append(sent)
                    start = i + new_start
                    continue

            # ignore 3dot seperators (assuming they do not seperate sentences) # TODO: CHANGE TO HANDLE SEQUENCE OF SEPERATORS
            elif (conc_sents[i:i + 3] == "..."):  # maybe add regex to ZEVEL arguments
                skip_until = i + 3
                #                input("DEBUG: 3DOT:\t")
                continue

            # assume space after seperators indicates of sentence seperation
            elif (re.match(pattern="\s", string=conc_sents[i + 1])):
                #                input("DEBUG: SEP_SPACE:\t"+ conc_sents[start:i+1] +"\tSTART: " + str(start))
                sent = conc_sents[start:i+1]
                sents.append(sent)
                # sent next start of sentence to the end of whitespaces sequences
                start = i + re.search(pattern=r"\s+?", string=conc_sents[i:]).end()
                continue

                # check sequnces between spaces
            else:
                # bound spaceless streak
                try:
                    i_next_space = i + re.search(pattern=r'\s+?', string=conc_sents[i:],
                                                 flags=(re.UNICODE)).start()
                except:
                    i_next_space = len(conc_sents)

                # determine if a sentence seperation occured in sequence (return first one's index if more than 1 occured)
                suspect = conc_sents[i_prev_space + 1 if start < i_prev_space else start:i_next_space]
                i_seperator = find_seperation(suspect, conc_sents[i])

                # no seperation was found in suspect skip until next white-space (legal world)
                if i_seperator == -1:
                    # no updates needed - skeep current sequnce
                    skip_until = i_next_space
                    pass  # TODO - not needed?

                # if there is a seperation - update indices and append relevant slice
                else:
                    sent = conc_sents[start:i_prev_space + 1 + i_seperator + 1]
                    sents.append(sent)
                    start = (i_prev_space + 1 if start < i_prev_space else start) + i_seperator + 1
                    continue  # TODO - not needed?
    # append last sentence no matter how it ends
    sents.append(conc_sents[start:len(conc_sents)])
    return sents

# constants and REGEXs ... move later somewhere
eng_letters_in_heb = ["איי","בי","סי","די","אי","אף","ג'י","אייץ'", "ג'יי","קיי","אל","אם","אן","או","פי","קיו","אר","אס","טי","יו","וי","אקס","איקס","ווי","זד","זי"] #for actonyms like "IBM" in hebrew
SENT_SEPERATORS = ["?","!","."]
QUOTE_MARKS = ["\'","\""]
MAX_LEN = 20


# regegx for seperation find ... maybe use as global ... TODO
GENDER_STUFF = [".ם ",".ן ","ת.ים ",".ות ",".ה ",".ית ",".ת "]
re_paran_open = r"[\(\[\{]*"
re_paran_close = r"[\)\]\}]*"
re_numeric = r"([(+-]?([0-9][0-9.,/\-:]*)?[0-9]%?)"
re_hebword = u"([\"\']?[א-ת]+[\"\']?[א-ת]+[\"\']?)"
re_hebrew_dash=re_hebword+"-"+re_hebword
re_heb_dot_acronym = u"((?:[א-ת]\.)+[א-ת]+)"
re_three_dot = u"..."
re_spaced_dot = u"\s\.\s"
re_numbering = "" # TODO
re_gender_neutral = "(" + re_hebword + "|".join(GENDER_STUFF) + ")"
re_heb_numeric = u"(([א-ת]+)([+-=_*]*)([0-9]+[0-9\.\/\\,:-]*)?[0-9]%?)"
re_legal_token = u"{}({})?{}".format(
    re_paran_open,
    "|".join((re_numeric,re_hebword,re_hebrew_dash,re_heb_dot_acronym,re_gender_neutral,re_heb_numeric)),
    re_paran_close)


def main():
   # get sources from the hebrew Ha'aretz treebank
   #  link_train = r"https://raw.githubusercontent.com/UniversalDependencies/UD_Hebrew-HTB/master/he_htb-ud-train.conllu"
   #  link_test = r"https://raw.githubusercontent.com/UniversalDependencies/UD_Hebrew-HTB/master/he_htb-ud-test.conllu"
   #  link_dev = r"https://raw.githubusercontent.com/UniversalDependencies/UD_Hebrew-HTB/master/he_htb-ud-dev.conllu"
   #
   #  link2file(link_dev,link_test,link_train)

    # load from files
    base_path = r"/home/yochay/Desktop/heb-tokenizer/"
#    base_path = os.getcwd()
    dev_path = base_path + "dev_sentences.txt"
    test_path = base_path + "test_sentences.txt"
    train_path = base_path + "train_sentences.txt"

    dev_sents, test_sents, train_sents = load_from_files(dev_path,test_path,train_path)

    # concatinate sentence with random spacings
    dev_conc = "".join(add_spaces(dev_sents))
    test_conc = "".join(add_spaces(test_sents))
    train_conc = "".join(add_spaces(train_sents))

    # seperate to sentences 250718
    dev_sep_sents = seperate2sents(dev_conc)
    test_sep_sents = seperate2sents(test_conc)
    train_sep_sents = seperate2sents(train_conc)

    #write results to files 250718
    sents2file(dev_sep_sents, dev_path.replace("txt", "seperated"))
    sents2file(test_sep_sents, test_path.replace("txt", "seperated"))
    sents2file(train_sep_sents, train_path.replace("txt", "seperated"))

    # seperate to list of sentences (as lists of words)
    # dev_list_of_sents_as_list_of_words = tokenize(dev_conc)
    # test_list_of_sents_as_list_of_words = tokenize(test_conc)
    # train_list_of_sents_as_list_of_words = tokenize(train_conc)


if __name__ == "__main__":
    main()

