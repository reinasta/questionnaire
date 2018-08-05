import csv
import sys
import itertools
from scipy.stats import chisquare
#import numpy as np

# some special features from mypy static typing library
from typing import Iterable

# convert a list of lists of quoted integers to a list of lists of integers.

def intify(xss):
    cs = []
    for xs in xss:
       ys = [int(item) for item in xs]
       cs += [ys]
    return cs

'''

The script takes two filenames as arguments, a csv file to read and another
file to write the results in. We convert the csv file to a reader-object and
that object to a list (of lists). We remove the column- and row-headers, and
then transpose the resulting list of lists, so that each sub-list represents
the evaluations per sentence (rather than per user). Optionally, we can write
this list to the file given as the second argument, if any such is given.

'''

with open(sys.argv[1], "rb") as infile, open(sys.argv[2], "wb") as outfile:
   reader = list(csv.reader(infile))[1:]         # skip the column-headers
   csvss_interim = map(list, zip(*reader))[1:]   # transpose & skip the row-headers
   csvss_per_question = intify(csvss_interim)    # converts string elements to ints
   outfile.write("\n\nAnalysis\n--------\n\n")
   #writer = csv.writer(outfile)                 # comment out to write the data to
   #for row in csvss_per_question: writer.writerow([item for item in row]) # outfile

# next step is to divide each set of evaluations in two categories (accepted,rejected).

def accepts_in(mylist) :
    return [x for x in mylist if x > 4]

def rejects_in(mylist) :
    return [x for x in mylist if x > 0 and x <= 4]

'''

 Takes a list of lists (answers) and outputs another; each of the sub-lists
 in the output list contains two integers representing the number of people
 that, respectively, accepted and rejected the sentence corresponding to the
 sub-list.

'''

def csvss_2categ(answers) :
    myanswers = []
    for answer in answers:
      answer = [[len(accepts_in(answer)), len(rejects_in(answer))]]
      myanswers += answer
    return myanswers

# The list containing lists of the form [number accepted, number rejected].

csvss_all = csvss_2categ(csvss_per_question)



# Sentences with pronouns (numbering reflects their order in questionnaire).

pros = [6,7,9,10,12,13,28,29,30,32,33] # sentence column numbers starting at 1

'''
The sentences in `pros` to be evaluated from 1-7 are those below. NB: the
background stories (contexts) against which the informants evaluated these
sentences are crucial. For those, see the paper and especially the survey.

6. Sue: Oscar trusts nobody. -- Pam: Not exactly, Oscar trusts *him*.
7. Sue: Oscar trusts nobody. -- Pam: Not exactly, Oscar trusts *himself*.
9. Everybody hates Lucifer. Only he (himself) likes him.
10. Everybody hates Lucifer. Only he likes himself.
12. Mary admires John, Sue admires him, and John admires *him* too.
13. Mary admires John, Sue admires him, and John admires *himself* too.
28. Only Max himself voted for him.
29. Only Max voted for him.
30. Only Max voted for himself.
32. Only Max himself voted for him.
33. Only Max voted for himself.

'''


'''

 Select the elements of `lists` according to whether they are members of the
 list of indices `inds` (adjusted for a count of indices that starts at 0)

'''

def elems_at(inds,lists) :
   cs = []
   for i in inds:
      xs = lists[i-1]
      cs += [xs]
   return cs

csvss_pro = elems_at(pros,csvss_all)

'''

 The expected number of people accepting or rejecting a given sentence.
 We use `exp_good` and `exp_bad` to represent sentences that are expected
 to be good and bad, respectively. NB: The numbers 5 and 25 reflect the
 possibility of error, that is the possibility that 20% of the people
 assessing a sentence which is good, mistake it for a bad one, and vice-versa.

NB: I'm also calculating the chi-sequared and p values with means as expectations.

'''

# since `chisquare` operates on columns rather than rows we transpose the list
csvss_pro_transposed = map(list,zip(*csvss_pro))

# results using means as expectations
results_uniform = chisquare(csvss_pro_transposed)

# when explicit results are given, we work with `csvss_pro`
exp_good = [25,5]
exp_bad = [5,25]

expected = [exp_good, exp_bad, exp_good, exp_bad, exp_good, exp_bad,
            exp_good, exp_good, exp_bad, exp_good, exp_bad]

# tuples of lists representing the observations and expectations (respectively)
observed_expected = zip(csvss_pro,expected)

def results_in(tuples):
   chis = []
   for (i,j) in tuples:
      chi2 = chisquare(f_obs=i,f_exp=j)
      chis += [chi2]
   return chis

# results using more realistic expectations
results_realistic = results_in(observed_expected)

print results_uniform
print results_realistic

# write the results to the filename given as the second argument
with open(sys.argv[2], "a") as f:
    f.write("\n\n\nUsing means as expectations:\n\n")
    f.write(str(results_uniform) + "\n\n")
    f.write("\n\n\nUsing more realistic expectations\n\n")
    f.write(str(observed_expected) + "\n\n")
    f.write(str(results_realistic) + "\n\n")

