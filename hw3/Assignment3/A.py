from main import replace_accented
from sklearn import svm
from sklearn import neighbors
import nltk
import re, string
import sys
from nltk.data import load

# don't change the window size
window_size = 10
pattern = re.compile('')

def get_stemmed_window(before, after, language):
    
    #http://stackoverflow.com/a/32469562/5606218
    from nltk.corpus import stopwords
    from nltk.tokenize import wordpunct_tokenize
    from nltk.stem.porter import PorterStemmer
    from nltk.stem import SnowballStemmer
    
    if language == 'english':
        stemmer = PorterStemmer()
    elif language == 'spanish':
        stemmer = SnowballStemmer("spanish")
    else:
        return [],[]
    
    stop_words = set(stopwords.words(language))
    stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}']) # remove it if you need punctuation 
    
    before = [stemmer.stem(i.lower()) for i in wordpunct_tokenize(before) if i.lower() not in stop_words][-window_size:]
    after = [stemmer.stem(i.lower()) for i in wordpunct_tokenize(after) if i.lower() not in stop_words][:window_size]
    
    return before, after

def get_plain_window(before, after):
    b = nltk.word_tokenize(before)[-window_size:]
    a = nltk.word_tokenize(after)[:window_size]
    return b, a

def get_POS_window(bp, word, ap):
        pos_tokens = nltk.pos_tag(ap + word + bp)
        offset = len(bp)
        
        bpos = pos_tokens[offset - window_size : offset]
        apos = pos_tokens[offset + 2 : offset + 2 + window_size]
        
        return [wtype for w, wtype in apos], [wtype for w, wtype in bpos]

# A.1
def build_s(data, language):
    '''
    Compute the context vector for each lexelt
    :param data: dic with the following structure:
        {
			lexelt: [(instance_id, left_context, head, right_context, sense_id), ...],
			...
        }
    :return: dic s with the following structure:
        {
			lexelt: [w1,w2,w3, ...],
			...
        }

    '''
    #sys.stdout.write('#')

    s = {}
    first = True
    for d in data:
        #print d
        s[d] = []
        for i in range(len(data[d])):
            lexelt = data[d][i]
            astem, bstem = get_stemmed_window(lexelt[1], lexelt[3], language)
            ap, bp = get_plain_window(lexelt[1], lexelt[3])
            s[d] += astem + bstem + ap + bp
            
        s[d] = set(s[d])
        """
        if first:
            print s[d]
            first = False
            
        
        if first < 1:
            index = 0
            for w in data[d][0]:
                print(str(index) + ": " + w + "\n")
                first += 1
                index += 1 
            before = nltk.word_tokenize(data[d][0][1])[-window_size:]
            after = nltk.word_tokenize(data[d][0][3])[:window_size]
            print("Before: " + str(before))
            print("After: " + str(after)) 
        else:
            exit()
        """
    
    

    # implement your code here

    return s


# A.1
def vectorize(data, s, language):
    '''
    :param data: list of instances for a given lexelt with the following structure:
        {
			[(instance_id, left_context, head, right_context, sense_id), ...]
        }
    :param s: list of words (features) for a given lexelt: [w1,w2,w3, ...]
    :return: vectors: A dictionary with the following structure
            { instance_id: [w_1 count, w_2 count, ...],
            ...
            }
            labels: A dictionary with the following structure
            { instance_id : sense_id }

    '''
    vectors = {}
    labels = {}

    #sys.stdout.write('.')
    
    # implement your code here
    for instance in data:
        instance_id = instance[0]
        labels[instance_id] = instance[4]
        astem, bstem = get_stemmed_window(instance[1], instance[3], language)
        ap, bp = get_plain_window(instance[1], instance[3])
        words = astem + bstem + ap + bp
        #words = []
        #words += nltk.word_tokenize(pattern.sub('', instance[1]))[-window_size:]
        #words += nltk.word_tokenize(pattern.sub('', instance[3]))[:window_size]
        
        vectors[instance_id] = [words.count(x) for x in s]
        
        if language == 'english':
            tags =  load('help/tagsets/upenn_tagset.pickle').keys()
            bpos, apos = get_POS_window(bp,[instance[2]],ap)
            vectors[instance_id] += [bpos.count(x) for x in tags]
            vectors[instance_id] += [apos.count(x) for x in tags]
        

    return vectors, labels


# A.2
def classify(X_train, X_test, y_train):
    '''
    Train two classifiers on (X_train, and y_train) then predict X_test labels

    :param X_train: A dictionary with the following structure
            { instance_id: [w_1 count, w_2 count, ...],
            ...
            }

    :param X_test: A dictionary with the following structure
            { instance_id: [w_1 count, w_2 count, ...],
            ...
            }

    :param y_train: A dictionary with the following structure
            { instance_id : sense_id }

    :return: svm_results: a list of tuples (instance_id, label) where labels are predicted by LinearSVC
             knn_results: a list of tuples (instance_id, label) where labels are predicted by KNeighborsClassifier
    '''
    #sys.stdout.write('.')

    svm_results = []
    knn_results = []

    svm_clf = svm.LinearSVC()
    knn_clf = neighbors.KNeighborsClassifier()

    # implement your code here
    svm_clf.fit(X_train.values(), y_train.values())
    knn_clf.fit(X_train.values(), y_train.values())

    svm_results = zip(X_test.keys(), svm_clf.predict(X_test.values()))
    knn_results = zip(X_test.keys(), knn_clf.predict(X_test.values()))
    
    #print(svm_results[0])
    #print(knn_results[0])
    
    return svm_results, knn_results

# A.3, A.4 output
import main
import os, errno
def print_results(results ,output_file):
    '''

    :param results: A dictionary with key = lexelt and value = a list of tuples (instance_id, label)
    :param output_file: file to write output

    '''

    # implement your code here
    # don't forget to remove the accent of characters using main.replace_accented(input_str)
    # you should sort results on instance_id before printing
    
    if not os.path.exists(os.path.dirname(output_file)):
        try:
            os.makedirs(os.path.dirname(output_file))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(output_file, "w") as outfile:
        for key in results.keys():
            #print(key)
            #print(results[key])
            for inst_tuples in results[key]:
                #print(inst_tuples)
                lexelt = main.replace_accented(key)
                instance_id = main.replace_accented(inst_tuples[0])
                label = inst_tuples[1]
                outfile.write( lexelt + ' ' + instance_id +  ' ' + label + '\n')


# run part A
def run(train, test, language, knn_file, svm_file):
    s = build_s(train, language)
    svm_results = {}
    knn_results = {}
    for lexelt in s:
        X_train, y_train = vectorize(train[lexelt], s[lexelt], language)
        X_test, _ = vectorize(test[lexelt], s[lexelt], language)
        svm_results[lexelt], knn_results[lexelt] = classify(X_train, X_test, y_train)

    print_results(svm_results, svm_file)
    print_results(knn_results, knn_file)



