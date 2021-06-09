from konlpy import init_jvm
from konlpy.tag import Okt
from collections import Counter
import networkx as nx

import re
import gensim
from gensim.models import Phrases
import itertools
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def make_edge(x, y, text, width):
    return  go.Scatter(x         = x,
                       y         = y,
                       line      = dict(width = width,
                                   color = '#FF0000'),
                       hoverinfo = 'text',
                       text      = ([None]),#text]),
                       mode      = 'lines')

def draw_networkx(tmp_content):                       
    f = open('./stop_words.txt', 'r')
    stop_words = f.readlines()
    f.close()
    pattern2= '[\n]'
    stop_words = list(map(lambda x: re.sub(pattern=pattern2, repl='', string=stop_words[x]), range(0, len(stop_words))))
    #print(stop_words)

    okt = Okt()
    tmp_nouns = []
    for i in range(0, np.shape(tmp_content)[0]):
        tmp_nouns.append(okt.nouns(tmp_content.content[i]))
    tmp_noun_list = []
    for sent in tmp_nouns:    
        sent_noun = []
        for w in sent:
            if w not in stop_words:
                sent_noun.append(w)
        tmp_noun_list.append(sent_noun)
    bigram = Phrases(tmp_noun_list, min_count=1, threshold=10)
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    docs = []
    for i in tmp_noun_list:
        tmp_i_ = bigram_mod[i]
        docs.append(tmp_i_)
    noun_list = list(itertools.chain.from_iterable(docs))
    noun_cnt = Counter(noun_list)
    noun_df = pd.DataFrame.from_dict((dict(noun_cnt)), orient='index').reset_index().rename(columns= {'index' : 'words', 0 : 'freq'})
    noun_df = noun_df.groupby(['words']).sum().reset_index()
    uniq_noun = Counter(dict(zip(noun_df['words'], noun_df['freq'])))
    uniq_key = list(uniq_noun.keys())
    noun_index = {noun : i for i, noun in enumerate(uniq_noun)}
    occurs = np.zeros([len(docs), len(uniq_noun)])

    for i, sent in enumerate(docs):
        for w in sent:
            index = noun_index[w]
            occurs[i][index] = 1
    co_occur = occurs.T.dot(occurs)

    G1 = nx.Graph()
    tmp_G1_node =[]
    for i in uniq_noun.keys():
        if uniq_noun[i] > 25:
            G1.add_node(i, size=uniq_noun[i])
            tmp_G1_node.append(i)
    for i in tmp_G1_node:#G1.nodes():
        ind_ = noun_index[i]    
        for j in range(0, occurs.shape[1]):
            if ind_ != j and co_occur[ind_][j] > 5:
                G1.add_edge(uniq_key[ind_], uniq_key[j], weight=co_occur[ind_][j])                
                
    pos_ = nx.kamada_kawai_layout(G1)
    edge_trace = []
    for edge in G1.edges():        
        char_1 = edge[0]
        char_2 = edge[1]
        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]
        text   = str(char_1) + '--' + str(char_2) + ': ' + str(G1.edges()[edge]['weight'])        
        trace  = make_edge([x0, x1, None], [y0, y1, None], text, 
                                   width = 1)#0.3*G.edges()[edge]['weight']**1)
        edge_trace.append(trace)
    node_trace = go.Scatter(x         = [],
                            y         = [],
                            text      = [],
                            textposition = "top center",
                            textfont_size = 10,
                            mode      = 'markers+text',
                            hoverinfo = 'none',
                            marker    = dict(color = [],
                                             size  = [],
                                             line  = None))    
    for node in G1.nodes():
        x, y = pos_[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['marker']['color'] += tuple(['#0000FF'])
        if 'size' in G1.nodes()[node]:
            node_trace['marker']['size'] += tuple([G1.nodes()[node]['size']])
        else:
            node_trace['marker']['size'] += tuple([0])
        node_trace['text'] += tuple(['<b>' + node + '</b>'])                
        
    return node_trace, edge_trace