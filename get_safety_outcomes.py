import os

def get_outcomes(env):

    dnn_dict = {}
    
    for directory in os.listdir(env):

        dnn_dict[directory] = []

        cur_dir = env + '/' + directory

        for run in os.listdir(cur_dir):

            run_name = cur_dir + '/' + run

            with open(run_name, 'r') as f:

                line_number = 1

                foundCrash = False

                for line in f:

                    items = line.split(',')

                    if int(items[len(items) - 1]) > 0:
                           dnn_dict[directory].append(line_number)
                           
                           foundCrash = True
                           break

                    line_number += 1

                if not foundCrash:
                    dnn_dict[directory].append(0)

    return dnn_dict
                           

if __name__ == '__main__':

    covered_dnn = get_outcomes('covered')
    uncovered_dnn = get_outcomes('uncovered')

    print('Safe outcomes in modified enviornment-----')

    for dnn in covered_dnn:

        num_crashes = 0
        total_runs = len(covered_dnn[dnn])

        for num in covered_dnn[dnn]:
            
            if num > 0:
                
                num_crashes += 1
        
        print(dnn + ': ' + str(total_runs - num_crashes) + '/' + str(total_runs))

    print('\n')

    print('Safe outcomes in unmodified enviornment-----')

    for dnn in uncovered_dnn:

        num_crashes = 0
        total_runs = len(uncovered_dnn[dnn])

        for num in uncovered_dnn[dnn]:
            
            if num > 0:
                
                num_crashes += 1
        
        print(dnn + ': ' + str(total_runs - num_crashes) + '/' + str(total_runs))    
