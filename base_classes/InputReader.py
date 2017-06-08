import numpy as np
import io
import re
import warnings
from TCI.lib.logger import logger

class InputReader:
    max_n_rows = 1e5
    def __init__(self):
        pass

    def read_clf(self, fname, headerexpr="Time.*Sig1[^\n]+",
                 compression=None):

        with io.open(fname, 'r', errors='replace') as f:
            text = f.read()
        self.text = text
        headerpos = self.findHeader(text, expr=headerexpr)
        if headerpos is None:
            return "No header", None

        header = text[headerpos[0]:headerpos[1]]
        names, units = self.parseHeader(header)

        raw_table_text = text[headerpos[1]:]
        values, comments = self.readUnstructuredTable(raw_table_text)
        return names, units, values, comments

    def findProperty(self, expr):
        position = self.findHeader(self.text, expr)
        text = self.text[position[1]:]
        expr = "[^\n]+"
        match = re.search(expr, text)
        param = text[match.start(): match.end()]
        return param

    def readUnstructuredTable(self, text):
        '''
        Reads a piece of text (string) that contains
        a table of data, some of which are numbers
        and some are strings
        '''
        # create a byte object cause that's what
        # genfromtxt gets
        data_bytes = io.BytesIO(text.encode())
        raw_data = np.genfromtxt(data_bytes, delimiter="\t",
                                 dtype=None)
        types = self._checkForConsistency(raw_data)

        # get types of the data in the table
        n_float_columns = 0
        n_string_columns = 0
        for t in types:
            if (t == np.float64):
                n_float_columns += 1
            elif (t == np.string_):
                n_string_columns += 1
            else:
                raise IOError("unknown type encountered")

        n_rows = raw_data.shape[0]
        n_columns = len(raw_data[0])

        number_data = np.zeros([n_rows, n_float_columns])
        if (n_string_columns > 0):
            string_data = np.empty([n_rows, n_string_columns],
                                   dtype="S10")
        else:
            string_data = None

        # write data into arrays
        for i in range(n_rows):
            row = raw_data[i]
            fj = 0  # current float column number
            sj = 0  # current string column number
            for j in range(n_columns):
                if (types[j] == np.float64):
                    number_data[i, fj] = row[j]
                    fj += 1
                elif (types[j] == np.string_ and
                      n_string_columns > 0):
                    string_data[i, sj] = row[j]
                    sj += 1

        return number_data, string_data

    def _checkForConsistency(self, table):
        '''
        checks whether each element of columns
        have particulare types
        Returns:
            type: list
                list of type of all columns
        Raises:
            AssertionError
                if some column element types are inconsistent
        '''
        n_rows = table.shape[0]
        n_columns = len(table[0])
        types = []
        for i in range(n_rows):
            row = table[i]
            assert len(row) == n_columns
            for j in range(n_columns):
                if (i == 0):
                    types.append(type(row[j]))
                else:
                    assert type(row[j]) == types[j], \
                        "%d-the column is inconsistent"
        return types

    def findHeader(self, text, expr="Time.*Sig1[^\n]+"):
        '''
        seeks for a regular expression reg
        in texts. returns header position in text
        '''
        match = re.search(expr, text)
        if match is None:
            return None
        return [match.start(), match.end()]

    def parseHeader(self, header):
        '''
	    Parces header of data
	    returns lists of names and units
	    '''
        entries = header.split("\t")
        names = []
        units = []
        unitless = []
        for e in entries:
            # print(e)
            sp = e.split()
            if (len(sp) == 1):
                unitless.append(sp[0])
            elif (len(sp) == 2):
                key = sp[0]
                # disable symbols that may have wierd symbols
                key = key.replace("-", "_")
                key = key.replace("+", "_")
                key = key.replace("/", "_")
                names.append(key)
                units.append(sp[1])
            else:
                raise NotImplementedError("strange entry %s" % e)

        return names, units

if __name__ == "__main__":
    fname = "_Training_Pc=1500 psi Sonic " + \
        "endcaps_Berea Mechanical Testing _2015-04-27_001.clf"
    import TCI
    test_data_path = TCI.__path__[0] + "/test/test-data/"
    fname = test_data_path + \
            "1500psi/" + \
            "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001.clf"
    reader = InputReader()
    output = reader.read_clf(fname)
    print(output)
