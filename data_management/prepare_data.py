from data_management import file_utils, parse_dataset
import os


def fetch_nzbi(dest):

    print('\nFetching: NCBI training and test set')

    training_ncbi = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItrainset_corpus.zip'
    file_utils.fetch_unpack_zip(training_ncbi, dest)
    test_ncbi = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItestset_corpus.zip'
    file_utils.fetch_unpack_zip(test_ncbi, dest)

    print('NCBI fetch complete\n')


def fetch_pre_w2v(dest):

    print('Fetching w2v pre-trained on pubmed, PMC, and wikipedia')
    print('This file is roughly 4 Gb so this will take some time ...')

    pretrained_wv = "http://evexdb.org/pmresources/vec-space-models/PubMed-and-PMC-w2v.bin"

    file_utils.fetch_url(pretrained_wv, dest)

    print('Pre-trained word2vec retrieved')


def main():

    dest = '../data/'

    fetch_nzbi(dest)

    train_path = dest + 'NCBI_train_processed.pkl.gz'

    parse_dataset.parse_dataset(dest + 'NCBItrainset_corpus.txt', train_path)

    data = file_utils.get_zipped_pkl_data(train_path)

    parse_dataset.parse_dataset(dest + 'NCBItestset_corpus.txt', dest + 'NCBI_test_processed.pkl.gz', data)

    #fetch_pre_w2v(dest)


if __name__ == "__main__":
    main()
