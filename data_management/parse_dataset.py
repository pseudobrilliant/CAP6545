import argparse
from data_management import nlp_utils, file_utils, data_utils
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import re


def clean(data):

    strip = re.sub('<category=.*?>', '', data)

    strip = strip.replace('</category>', '')

    return strip


def get_categories(content, tags, categories):

    sent_cat = []

    tag_count = len(tags)

    while True:

        if not content:
            return sent_cat
        line = content[0]
        content.pop(0)

        if line == '\n':
            return sent_cat
        values = line.split('\t')
        name = values[3]
        tag = values[4]

        if 'B-' + tag not in tags:
            tags['B-' + tag] = tag_count
            tags['I-' + tag] = tag_count + 1

            tag_count += 2

        if name not in categories:
            categories[name] = tag

        if name not in sent_cat:
            sent_cat.append(name)


def get_tokenized(sentences, pos_dic):

    post = []
    wordt = []

    for sentence in sentences:
        words = nlp_utils.sentence_cleanup(sentence)

        if len(words) == 0:
            continue

        tokenized_pos = nlp_utils.pos_tag(words)

        encoded_pos = []

        for w, pos in tokenized_pos:
            if pos not in pos_dic:
                pos_dic[pos] = len(pos_dic) + 1

            encoded_pos.append([pos_dic[pos]])

        post.append(encoded_pos)
        wordt.append(words)

    return wordt, post


def get_sentences(content):

    sentences = []

    for i in range(2):
        line = content.pop(0)
        line = re.sub('\d+\|[a|t]\|', '', line)
        sentences += nlp_utils.sent_tokenize(line)

    return sentences


def get_lines(content_path):

    with open(content_path, 'r') as f:

        return f.readlines()


def get_iob_tags(sentences, cur_categories, categories):

    total_iob = []

    for sentence in sentences:

        sent_iob = ['O' for word in sentence]

        for cat in cur_categories:

            cat_split = cat.split(' ')

            if set(cat_split).issubset(sentence):
                cat_index=[]
                cat_group=[]
                cur_found = 0

                for i in range(len(sentence)):

                    if cur_found == len(cat_split):
                        cur_found = 0
                        cat_index.append(cat_group)
                        cat_group = []

                    if sentence[i] == cat_split[cur_found]:
                        cat_group.append(i)
                        cur_found += 1
                    else:
                        cur_found = 0
                        cat_group = []

                for cat_group in cat_index:
                    for i in range(len(cat_group)):
                        if i == 0:
                            if sent_iob[cat_group[i]] != 'O':
                                continue
                            sent_iob[cat_group[i]] = 'B-' + categories[cat]
                        else:
                            sent_iob[cat_group[i]] = 'I-' + categories[cat]

        total_iob.append(sent_iob)

    return total_iob


def get_enc_tags(tokenized_tags, tags):

    sentences_enc = []

    for sent in tokenized_tags:
        encoded = []

        for tag in sent:

            enc = tags[tag]

            onehot = [0.0 for i in tags]

            encoded.append([enc])

        sentences_enc.append(encoded)

    return sentences_enc



def parse_dataset(content, save, past_run=None):

    print("Parsing file at " + content)

    lines = get_lines(content)

    if lines[0] == '\n':
        lines.pop(0)

    total_sentences = []

    tags = {'O': 0}

    categories = dict()
    pos_dict = dict()

    if past_run:
        tags = past_run['tags']
        pos_dict = past_run['pos_dict']
        categories = past_run['categories']

    tokenized_words = []
    tokenized_pos = []
    tokenized_tags = []

    while lines:
        sentences = get_sentences(lines)

        cur_cat = get_categories(lines, tags, categories)

        (twords, tpos) = get_tokenized(sentences, pos_dict)

        tokenized_words += twords

        tokenized_pos += tpos

        tokenized_tags += get_iob_tags(twords, cur_cat, categories)

        total_sentences += sentences

    max_sent_length = data_utils.padding(tokenized_words, '<None>', 104)

    data_utils.padding(tokenized_tags, 'O', 104)

    data_utils.padding(tokenized_pos, [0], 104)

    char, max_word_length, char_dict = data_utils.get_padded_chars(tokenized_words, 42)

    enc_tags = get_enc_tags(tokenized_tags, tags)

    processed_data = {"excepts": total_sentences, "categories": categories, 'tags': tags, "words": tokenized_words,
                      "char": char, "char_dict": char_dict, "pos_dict":pos_dict, "pos": tokenized_pos,
                      'tok_tags': tokenized_tags, 'enc_tags': enc_tags, 'max_sent': max_sent_length,
                      'max_word': max_word_length}

    file_utils.zip_pkl_data(processed_data, save)

    print("Completed Parsing\n")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--content", "-c", help="File to tokenize", required=True)
    parser.add_argument("--save", "-s", help="Save tokenized as", required=True)
    parser.add_argument("--dictionary", "-d", help="Dictionary file", required=False)

    args = parser.parse_args()

    if args.dictionary:
        data = file_utils.get_zipped_pkl_data(args.dictionary)
        parse_dataset(args.content, args.save, data)
    else:
        parse_dataset(args.content, args.save)

if __name__ == "__main__":
    main()
