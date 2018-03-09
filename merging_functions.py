import pandas as pd
import numpy as np
import os
import editdistance
years = range(1790, 2020, 10)


def state_wikipedia_data(stateabbr):
    st = pd.read_csv("wikipedia_state_data/{}.csv".format(stateabbr))
    st = st[st.settlement_type != "County"]
    st = st[st.settlement_type != "US County"]
    mat = np.array(st[['y' + str(y) for y in years]])
    for y in years:
        del st['y' + str(y)]
    mat[np.isnan(mat)] = 0
    st['wiki_pops'] = [",".join(np.char.mod('%i', mat[i][::-1])) for i in range(len(mat))]
    mat[mat==0] = np.nan 
    return (st, mat)


# Alperin stuff

fs = [f for f in os.listdir("wiki_census/") if f.endswith(".csv")]
fs.sort()
master_list = []
last = "XXf"
for f in fs:
    if f[:2]!=last[:2]:
        master_list.append(f)
    else:
        # which is bigger?
        if os.path.getsize("wiki_census/" + master_list[-1]) > os.path.getsize("wiki_census/" +f):
            continue
        else:
            master_list[-1] = f
    last = f




complete_alperin_set = pd.DataFrame([])
for f in master_list:
    new_data = pd.read_csv("wiki_census/" + f,na_values = ["-","(X)"," "])
    new_data["state"] = f[:2]
    if 'CENSUS2010POP' in new_data.columns:
        new_data['2010'] = new_data['CENSUS2010POP']
        del new_data["CENSUS2010POP"]
    for t in ["COUNTY","County"]:
        if t in new_data.columns:
            new_data["Alperin_County"] = new_data[t]
            del new_data[t]
    for t in ["Geography","NAME","Name","Place"]:
        if t in new_data.columns:
            new_data["Alperin_Place"] = new_data[t]
            del new_data[t]
    for t in ["Geography","NAME","Name","Place"]:
        if t in new_data.columns:
            new_data["Alperin_Place"] = new_data[t]
            del new_data[t]
    for t in ["STATE","STNAME","State",'2014','2015']:
        if t in new_data.columns:
            del new_data[t]
    complete_alperin_set = complete_alperin_set.append(new_data)


 
alperin_mat = np.array(complete_alperin_set[[str(y) for y in years]])
alperin_mat[np.isnan(alperin_mat)] = 0
for y in years:
    del complete_alperin_set[str(y)]
complete_alperin_set['alperin_pops'] = [",".join(np.char.mod('%i', alperin_mat[i][::-1])) for i in range(len(alperin_mat))]

for cname in complete_alperin_set.columns:
    if "ESTIMATE" in cname:
        del(complete_alperin_set[cname])

alperin_mat[alperin_mat==0] = np.nan


CESTA = pd.read_excel("1790-2010_MASTER.xlsx")

# Some CESTA data doesn't work so great.

CESTA["2010"] = pd.to_numeric(CESTA["2010"],np.float64)
CESTA["1910"] = pd.to_numeric(CESTA["1910"],np.float64)
CESTA["1980"] = pd.to_numeric(CESTA["1980"],np.float64)
cesta_mat = np.array(CESTA[[str(y) for y in years]])

for y in years:
   del CESTA[str(y)]

cesta_mat[np.isnan(cesta_mat)] = 0
CESTA['cesta_pops'] = [",".join(np.char.mod('%i', cesta_mat[i][::-1])) for i in range(len(cesta_mat))]

cesta_mat[cesta_mat==0] = np.nan
def CESTA_Version(st="ME"):
    return (CESTA[CESTA.ST==st],cesta_mat[CESTA.ST == st])


def state_counts(st = "ME"):
    # Generate similarly-formatted data for all three formats
    alperin_model = (complete_alperin_set[complete_alperin_set["state"]==st], alperin_mat[complete_alperin_set["state"] == st])
    wiki_model = state_wikipedia_data(st)
    cesta = CESTA_Version(st)
    return (alperin_model, wiki_model, cesta)


    # (202) 224-3121

class Citymatch(dict):
    dict = {}
    
    def keep_score(self):
        # Ranking, in order, use:
        # 1. overlap percent
        # 2. Total overlaps
        # 3. String distance
        return (
            float(self['n_matches'])/self['possible_overlaps'],
            self['n_matches'],
            # Negative since lower editdist is better.
            -editdistance.eval(*self.names())
        )

    def __cmp__(self,other):
        return cmp(self.keep_score(), other.keep_score())

    def __repr__(self):
        a_name,b_name = self.names()
        return "{}=={} (a{}==b{}) ({}/{} matches)".format(a_name,b_name,self["a"],self["b"],self["n_matches"],self["possible_overlaps"])
    
    def names(self):
        names = []
        for pos in ['a','b']:
            for k in ["title","CityST","Alperin_Place"]:
                try:
                    i = self[pos]
                    names.append(
                        self["sources"][pos].iloc[i][k]
                        )
                    break
                except KeyError:
                    pass
                except AttributeError:
                    print pos
                    print self['sources']
                    raise
        return names
                    
            
def match_row(a,b,i,min=3,sources = (None,None)):
    matches = np.sum(a == b[i],axis=1)
    # First find even single matches.
    l = list(np.where(matches>0)[0])
    oput = []
    for j in l:
        # The sum of the true-false product is just the number
        # of overlapping non-zero values.
        possible_overlaps = np.sum((a[j] > 0) * (b[i] > 0))
        # Use single matches if they're the only data. 
        if matches[j] > min or matches[j]==possible_overlaps:
            m = Citymatch(
                {"a":i,
                 "b":j,
                 "n_matches":matches[j],
                 "possible_overlaps": possible_overlaps,
                 "sources":{
                     "a":sources[0],
                     "b":sources[1]
                 }
                }
            )
            oput.append(m)
    return oput
    
from collections import defaultdict
import editdistance

def match_matrices(b,a,min=3,sources=(None,None)):
    a_lengths = np.sum(a > 0,axis=1)
    b_lengths = np.sum(b > 0,axis=1)
    matches = []
    for i in range(len(b)):
        row_matches = match_row(a,b,i,min=min,sources=sources)
        matches += row_matches

    print "{} matches between the sets".format(len(matches))
    # Make sure nothing matches twice.
    # This might happen when--e.g.--Manhattan
    # and New York City have the same population
    # for 100 years, but then diverge.
    
    a_s = defaultdict(list)
    b_s = defaultdict(list)

    for i,m in enumerate(matches):
        a_s[m['a']].append(m)
        b_s[m['b']].append(m)    

    kill_list = set([])

    for vs in b_s.values() + a_s.values():
        vs.sort()
        vs.reverse()
        for v in vs[1:]:
            kill_list.add((v['a'],v['b']))

    return [m for m in matches if not (m['a'],m['b']) in kill_list]

    


## Filling of NA values

def fill_na_point(array,i):
    array = np.log(array)
    #i: the point to be filled.
    non_zeros = np.where(np.isfinite(array))[0]
    try:
        w = np.max(non_zeros[non_zeros < i])
    except ValueError:
        y = np.min(non_zeros[non_zeros > i])
        return np.exp(array[y])
    try:
        y = np.min(non_zeros[non_zeros > i])
    except ValueError:
        return np.exp(array[w])
    if array[w]==array[y]:
        # kludge b/c numpy can't fill out a sequence with step of zero.
        fill = [array[w]]*100
    else:
        fill = np.arange(array[w], array[y], step = (array[y] - array[w])/(y-w))
    if len(fill)==0:
        print fill,array
        raise
    return np.exp(fill[i-w])

    
def fill_nas(joint):
    # Interpolate missing points as a geometric mean of the nearest non-na points.
    # Edges are just identical
    clone = np.copy(joint)
    missing = np.where(np.isnan(joint))[0]
    for i in missing:
        clone[i] = fill_na_point(joint,i)
    return clone


def merge_a_match(match,a_mat,b_mat):
    # match: an array match item.
    a = a_mat[1][match['a']]
    b = b_mat[1][match['b']]

    joint = []
    
    for (a_,b_) in zip(a,b):
        if a_==b_:
            joint.append(a_)
        elif np.isnan(a_):
            # OK if this too is nan.
            joint.append(b_)
        elif np.isnan(b_):
            # OK if this too is nan.
            joint.append(a_)
        else:
            joint.append(np.nan)

    joint = np.array(joint)
    # fill estimates by interpolating linear growth rates.
    try:
        estimates = fill_nas(joint)
    except:
        print joint
        raise
        # Put the originals side by side.
    besides = np.array([a,b])
    # fill nas to infinity to avoid raising errors.
    besides[np.isnan(besides)] = 2e10
    # the better guess minimizes distance from the estimates
    which_to_pick = np.nanargmin(np.abs(besides - estimates),0)

    best_guess = np.array([besides[j,i] for i,j in enumerate(which_to_pick)])
    best_guess[np.isnan(best_guess)] = 0
    best_guess[best_guess > 1e10] = 0
    return best_guess


def merge_two_sets(a,b):
    # a and b are both tuples of a dataframe and a matrix of populations.
    # This returns a new dataframe.
    matches = match_matrices(a[1],b[1],min=2,sources=(a[0],b[0]))
    as_a = set([m['a'] for m in matches])
    as_b = set([m['b'] for m in matches])

    only_b = set(range(len(b[1]))).difference(as_b)
    only_a = set(range(len(a[1]))).difference(as_a)

#    if (len(only_a)==0):
#        # In case one is empty, like Hawaii for Alperin.
#        return merge_two_sets(b,a)

    
    new_frame = []

    new_pops = np.zeros((len(matches) + len(only_a) + len(only_b), 23))

    i = 0
    for match in matches:
        new_pops[i] = merge_a_match(match,a,b)
        d1 = a[0].iloc[match['a']].to_dict()
        d2 = b[0].iloc[match['b']].to_dict()
        d1.update(d2)
        new_frame.append(d1)
        i += 1

    if only_a:
        for j, akey in enumerate(only_a):
            new_pops[i + j] = a[1][akey]
            new_frame.append(a[0].iloc[akey].to_dict())
            j += 1
    else:
        j = 0
    for k, bkey in enumerate(only_b):
        new_pops[i + j + k] = b[1][bkey]
        new_frame.append(b[0].iloc[bkey].to_dict())
        
    new_joint = pd.DataFrame(new_frame)

    return new_joint,new_pops
