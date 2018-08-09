import os
import random
import re
import requests

REG_SEN = re.compile(r'# text = (.*)\n')

# url --> [sentences]
def link2sent_list(link) -> [str]:
    contents = requests.get(link)
    contents = contents.text
    sents = REG_SEN.findall(contents)
    return sents

def conc_sents(sentsList):
    spaced_sents = []
    for i in range(len(sentsList)):
        num_of_spaces = random.sample([0,1],1)[0]
        spaced_sents.append(sentsList[i] + num_of_spaces * " ")
    return "".join(spaced_sents)


def string2file(string, path):
    with open(path,'wt',encoding='utf8') as f:
        f.write(string)


def main():
    # download sentences from haaretz treebank
    link_train = r"https://raw.githubusercontent.com/UniversalDependencies/UD_Hebrew-HTB/master/he_htb-ud-train.conllu"
    link_test = r"https://raw.githubusercontent.com/UniversalDependencies/UD_Hebrew-HTB/master/he_htb-ud-test.conllu"
    link_dev = r"https://raw.githubusercontent.com/UniversalDependencies/UD_Hebrew-HTB/master/he_htb-ud-dev.conllu"
    train_sents, test_sents, dev_sents = link2sent_list(link_train), link2sent_list(link_test), link2sent_list(link_dev)

    # create random spacing concatination
    train_conc , test_conc , dev_conc = conc_sents(train_sents), conc_sents(test_sents), conc_sents(dev_sents)

    # write concatinated sentences to file
    string2file(train_conc, os.path.sep.join((os.getcwd(),"data","train.conc")))
    string2file(test_conc, os.path.sep.join((os.getcwd(),"data","test.conc")))
    string2file(dev_conc, os.path.sep.join((os.getcwd(),"data","dev.conc")))


if __name__ == '__main__':
    main()