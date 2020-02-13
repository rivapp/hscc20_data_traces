from six.moves import cPickle as pickle
import matplotlib.pyplot as plt
import numpy as np

def get_num_small(errs):

    small_errs = []

    for err in errs:

        if err <= 0.05:

            small_errs.append(err)

    return small_errs

reflected_covered_pickle = 'reflected_covered.pickle'
errors_covered_pickle = 'errors_covered.pickle'

reflected_uncovered_pickle = 'reflected_uncovered.pickle'
errors_uncovered_pickle = 'errors_uncovered.pickle'

with open(reflected_covered_pickle, 'rb') as f:

    num_reflected_covered = pickle.load(f)

with open(reflected_uncovered_pickle, 'rb') as f:

    num_reflected_uncovered = pickle.load(f)    

with open(errors_covered_pickle, 'rb') as f:

    all_errors_covered = pickle.load(f)

with open(errors_uncovered_pickle, 'rb') as f:

    all_errors_uncovered = pickle.load(f)        

print('average number of missing rays covered: ' + str(np.mean(num_reflected_covered)))
print('average number of missing rays uncovered: ' + str(np.mean(num_reflected_uncovered)))

print('average error covered: ' + str(np.mean(all_errors_covered)))
print('average error uncovered: ' + str(np.mean(all_errors_uncovered)))

print('maximum error covered: ' + str(np.max(all_errors_covered)))
print('maximum error uncovered: ' + str(np.max(all_errors_uncovered)))

print('variance error covered: ' + str(np.var(all_errors_covered)))
print('variance error uncovered: ' + str(np.var(all_errors_uncovered)))

small_errs_covered = get_num_small(all_errors_covered)
small_errs_uncovered = get_num_small(all_errors_uncovered)

print('proportion of 5cm errors in covered environment: ' + str(float(len(small_errs_covered)) / len(all_errors_covered)))
print('proportion of 5cm errors in uncovered environment: ' + str(float(len(small_errs_uncovered)) / len(all_errors_uncovered)))

#fig = plt.figure()

#plt.xlim((0,0.5))
#plt.hist(all_errors_covered)

#plt.show()

#print(dir(plt))
