import numpy as np

def write_csv(keys, data, fname='.csv'):
    '''
    Input:
    keys: string list
    data: list of 1d np.arrays or python lists
    fname: string
    '''
    # compute the lengths of each array in data
    n_cols = len(data)
    lens = np.zeros(n_cols, dtype='int')
    for c in range(len(data)):
        lens[c] = len(data[c])
    # write file
    with open(fname, 'w') as f:
        # write header
        for key in keys:
            f.write(key)
            f.write("\t")
        f.write("\n")
        # write data
        for i in range(lens.max()):
            for c in range(n_cols):
                if (i < lens[c]):
                    f.write(str(data[c][i]))
                f.write("\t")
            f.write("\n")
