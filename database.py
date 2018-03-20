import readline
import time
import cmd
import csv
import pickle

class UserEscape(Exception):
    pass

class Field:
    '''
    stud = Field('student', place='fields/', handle='upi') ... creates a database of students,
    with user-assignable attributes, all stored in a file called 'fields/student.p'
    and accessed via a compulsory "handle" attribute called 'upi'. If the file supplied
    already exists (through a previous instantiation and call to
    the save() method) then the database is restored from that file and the value of handle, if supplied,
    is ignored (and instead extracted from the file). Otherwise a new file is created.

    The first parameter, 'student', in the instantiation above is stored as the attribute stud.title
    and is used as a prefix for keys created for each record (see "stud.key('abla070')" below). 

    stud.add('abla070') ... add a new student to the database with 'upi' attribute
    'abla070'. If one already exists, none is added and the call returns False.

    stud['abla070'] ... a mutable dictionary of attributes for the student with the attribute
    'upi' equal to 'abla070'. For example, {'upi':'abla070', 'gender': 'male'}. The values can have any type
    but the keys (attribute names) should be strings or integers. 

    stud.key('abla070') ... a unique key of string type associated with the record for 'abla070',
    which can be used in databases referring to students in the database stud. The key is created
    when 'abla070' is first added to the database. The 'upi' attribute 'abla070' can be modified
    but the key for the record remains constant, as in the following:

      stud['abla070']                       # {'upi':'abla070', 'age': 45}
      stud.key('abla070')                   # 'student_8567'
      stud['abla070']['upi'] = 'a.blaom'     
      OOOPS: NOT TRUE; BINDING OF KEY TO NEW HANDLE IS NOT CHANGED UNTIL REINSTANTIATION
      stud['abla070']                       # KeyError: 'abla070'
      stud['a.blaom']                       # {'upi':'a.blaom', 'age': 45}
      stud.key('a.blaom')                   # 'student_8567'

    stud.lookup('student_8567') ... the current 'upi' of the student record with permanent
    key 'student_8567'. In the preceding example:

      stud.lookup('student_8567')            # 'a.blaom'
    
    stud.save() ... save the database to file

    stud.handles() ... a list of the 'upi' of each student

    stud.has_handle('a.blaom') ... True if 'a.blaom' is the current 'upi' of a student in the
    database; False otherwise.

    The database can be iterated, the iterator returning the handles in the database, one at a time:
    
       for s in stud:
           print stud[s][age]

    will print out the age of every student in the database.     
    
    stud.read('stage1.csv') ... Read records into the database from a comma-separated file
    containing a header of attributes. If 'upi' is not among these attributes, or if there
    is a problem opening the file, then False is returned. File records for students with a upi
    already in the database are overwritten, unless one uses the alternative call
    'stud.read('stage1.csv', update=False).

    
    stud.input('Enter a student upi: ') ... Prompt the user to choose a student by entering its 'upi'
    (the attribute established as a handle for students at instantiation). The user is offered 
    autocompletion. The student's 'upi' is returned:

      handle = stud.input('Enter a student upi: ')     # Enter a student upi: a.blaom
      handle                                           # a.blaom

    If the optional prompt is omitted then a prompt is synthesized from the two strings provided during
    the (first) instantiation.

    stud.edit('a.blaom') ... Enter an interactive editor for the attributes of student with upi 'a.blaom'
    It only allows the editing of attribute values of string or numeric type. For other types use
    stud._edit('a.blaom') and enter the new value exactly as a python object.

    stud.edit() ...  Same as above but first the user is prompted interactively for the student
    whose attributes are to be edited 

    stud._records ... the dictionary of student records (each a dictionary itself), keyed
    on the unique string-type keys discussed above:

      stud._records['student_857']            #   {'upi':'a.blaom', 'age': 45}

    '''
    
    def __init__(self, title, handle = None, place = ''):
        # note that handle has different meaning here and in the
        # _load() method. Here it is the name of the attribute to be
        # used as a handle. Elsewhere in the code it is the value of that attribute
        self.title = title
        self._place = place
        try:
            self._load(handle)
        except (EOFError, IOError):
            if handle == None:
                print('Error. This is a new database. You must therefore supply a handle' + 'attribute')
                return
            else:
                self._handle_attribute = handle
                self._records = {}
                self._maxindex = 0
                self.save()
        self._update_glossary()
        
    def __repr__(self):
        string = ''
        for handle in self.handles():
            string = string + str(handle) + '  '
        string = string + ''
        return string
#        return str(self.title)
    def _update_glossary(self):
        self._glossary = {}
        for key in self._records.keys():
            handle = self.lookup(key)
            self._glossary[handle] = key
    def lookup(self, key):
        return self._records[key][self._handle_attribute]
    def key(self, handle):
        return self._glossary[handle]
    def handles(self):
        return self._glossary.keys()
    def has_handle(self, handle):
        return self._glossary.has_key(handle)
    def __getitem__(self, handle):
        return self._records[self.key(handle)]
    def __iter__(self):
        for k in self._records.keys():
            yield self.lookup(k)
    def add(self, handle):
        if self.has_handle(handle):
            return False
        else:
            self._maxindex += 1
            key = self.title + '_' + str(self._maxindex)
            self._records[key] = {self._handle_attribute:handle}
            self._glossary[handle] = key
            return True
    def _load(self, handle):
        filename = self._place + self.title + '.p'
        self._records, self._maxindex, temp = pickle.load(open(filename, 'r'))
        # if handle != None:
        #     print 'Supplied handle attribute ignored.'
        self._handle_attribute = temp
    def save(self):
        filename = self._place + self.title + '.p'
        pickle.dump((self._records, self._maxindex, self._handle_attribute), open(filename, 'w'))
    def read(self, filename, update=True):
        try:
            file = open(filename, 'rU') # the 'U' means various EOL characters are all understood
        except IOError:
            print 'Error. Unable to open \'' + filename + '\'.'
            return False
        csv_file = csv.reader(file)
        header = csv_file.next()
        if self._handle_attribute not in header:
            print('Error. File does not contain the key attribute \'' +
                   self._handle_attribute + '\'. No data read.' )
            return False
        else:
            for line in csv_file:
                record = {}
                for i in range(len(line)):
                   record[header[i]]=line[i]
                handle = record[self._handle_attribute]
                if self.add(handle) == False and update == False:
                    print('Record with ' + self._handle_attribute + '='
                          + handle + ' already exists and was not updated.')
                else:
                    for attribute in header:
                       self[handle][attribute]=record[attribute]
            self._update_glossary()
            return True
        file.close()
    def input(self, prompt=None):
        if prompt == None:
            prompt = self._handle_attribute + ' of ' + self.title + ': '
        options = self.handles()
        options.append('escape')
        handle = auto_input(prompt, options)
        return handle
    def edit(self, handle=None):
        if handle == None:
            handle = self.input()
            if handle == 'escape':
                print 'Input cancelled.'
                print 'No changes made.'
                return
        record =  self[handle]
        def complete(text, state):
            for option in record:
                if option.startswith(text):
                    if not state:
                        return option
                    else:
                        state -= 1
        readline.parse_and_bind(parse_instruction())
        readline.set_completer(complete)
        valid_input = False
        show(record)
        while not valid_input:
            print 'ATTRIBUTES: '
            for attribute in record:
                print attribute,
            print '\n'
            attribute = raw_input('Attribute to be modified: ')
            t = type(record[attribute])
            if attribute not in record.keys():
                print 'Unknown attribute.'
            elif t is not str and t is not int and t is not float:
                print 'Sorry. Only string or numeric type attributes can be edited.'
            else:
                valid_input = True
        print 'Current value of attibute: ' + str(record[attribute])
        record[attribute] = raw_input('New value of attribute: ')
        if attribute == self._handle_attribute:
            self._update_glossary()
        show(record)
    def _edit(self, handle=None):
        if handle == None:
            handle = self.input()
            if handle == 'escape':
                print 'Input cancelled.'
                print 'No changes made.'
                return
        record =  self[handle]
        def complete(text, state):
            for option in record:
                if option.startswith(text):
                    if not state:
                        return option
                    else:
                        state -= 1
        readline.parse_and_bind(parse_instruction())
        readline.set_completer(complete)
        valid_input = False
        isnew = False
        show(record)
        while not valid_input:
            print '\n'
            print 'ATTRIBUTES: ',
            for attribute in record:
                print attribute,
            print '\n'
            attribute = raw_input('Attribute to be modified (enter * to add attribute): ')
            if attribute not in record.keys():
                if attribute == '*':
                    attribute = raw_input('Name of new attribute: ')
                    valid_input = True
                    isnew = True
                else:
                    print 'Unknown attribute.'
            else:
                valid_input = True
        if isnew is False:
            print 'Current value of attibute: ' + repr(record[attribute])
        else:
            record[attribute] = input('New value of attribute AS PYTHON OBJECT: ')
        if attribute == self._handle_attribute:
            self._update_glossary()
        print '\n'
        show(record)


    
class Journal:
    '''
    In the example below <activities>, <students>, and <courses> are Field instances. For example, we have
    
       activities.handles()    # ['test', 'play time']
       students.handles()      # ['abla070', 'bbbb999']
       courses.handles()         # ['108', '150', '208']
       
    The handle attributes are 'name', 'upi' and 'name' respectively.

    j = Journal('My log book', place='data/', fields = [activities, students, courses]) ... instantiates a
    journal, <j>, entitled 'My log book'. Each entry of this journal will consist of a selection from the
    compulsory field <activities> and any number of selections from the fields <students> and <courses>.
    The compulsory `event' field (here <activities>) must appear first in the list parameter <fields>. Every
    record of <activities> (e.g., the activity with handle 'test') must possess an attribute called 'fields'
    which will be a list of names of attributes associated with all such activities (e.g., 'mark out of 100',
    'grade'). 

    Journal entries are made in steps using the methods open(), build(), add() and close(). A call to open()
    promts the user for a selection from the event field, here <activities>. The build() call promts the user
    to supply values to each attribute in the 'fields' attribute of the chosen activity. The add() method
    prompts the user to choose a value for one of the optional fields (e.g, <students>). The close() method
    completes the journal entry. Before closing the entry can be reviewed with the show() method. To save to
    file requires a call to the save() method after closing. Here is an example
    of how journal methods are made:

        j.open()  #  name of activity:
        test      #
        j.build() #  mark out of 100:
        45.2      #  
        y
        j.add('student')  # upi of student:
        abla070
        j.add()   # Field (<tab> for choices):
        course    # Name of course:
        108
        j.show()  # test  abla070  108  mark out of 100 = 45.2
        j.close()
        j.show()  #
        j.save()

    One can also give open() an explicit argument, eg j.open('test').
    User escape: In calls to open(), build() and add() the user has the opportunity to enter 'escape'
    at any time during input. In that the excpetion UserEscape is raised. ANY USER OF THIS LOG CLASS
    MUST HAVE A HANDLER FOR THIS EXCEPTION WITH ANY SUCH CALLS.

    j.del_last() ... removes the last entry made in the journal
    j.del_last(5) ... removes the last 5 entries made in the journal
    
    The items returned on an iteration of the Journal j are the times (in seconds since 1970) of
    journal entries. For such a time t one gets the corresponding record with j[t]. A record is a pair
    whose elements are a list of coded values of fields, beginning with the value of the `event'
    field, and a dictionary storing the values of the attributes associated with that event:

       for t in j:
          print t, j[t]

    produces the following output:
   
       593472349.4423847 (['activity1', 'student2'], {'mark out of 100':45.2})
       etc
    
    '''
    
    def __init__(self, title, place='', fields=None):
        self._open = False
        self.title = title
        self._place = place
        self._fields = fields
        self._current_list = []
        self._current_dictionary = {}
        try:
            self._load()
        except (EOFError, IOError):
            self._records = {}
            self.save()
        self._events = fields[0]
        self._glossary = {}
        for f in self._fields:
            self._glossary[f.title] = f
        self.reset_filter()
    def __getitem__(self, time):
        return self._records[time]
    def __iter__(self):
        for t in sorted(self._records.keys()):
            yield t
    def _load(self):
        filename = self._place + self.title + '.p'
        self._records = pickle.load(open(filename, 'r'))
    def write(self, coded_list, dictionary):
        t = time.time()
        self._records[t]= (coded_list, dictionary)
    def show(self):
        self._show(self._current_list, self._current_dictionary)
    def _show(self, l, d):
        for k in l:
            field = self._glossary[prefix(k)]
            handle = field.lookup(k)
            print (handle + '  '),
        for k in d:
            print k + ' = ' + str(d[k]) + '  ',
        print ''
    def open(self, event=None):
        if event == None:
            event = self._events.input()
            if event == 'escape':
                raise UserEscape('Abandoning new entry creation')
        self._current_list.append(self._events.key(event))
        self._open = True
    def build(self):
        if len(self._current_list) == 0:
            return False
        else:
            event = self._events.lookup(self._current_list[0])
            fields = self._events[event]['fields']
            if len(fields) != 0:
                self._current_dictionary = dict_input(fields)
            return True
    def add(self, field_title=None):
        if field_title == None:
            options = []
            for opt in self._glossary:
                if opt != self._events.title:
                    options.append(opt)
            options.append('escape')
            field_title = auto_input('Field (<tab> for options): ', options)
            if field_title == 'escape':
                raise UserEscape('Abandoning new entry creation')
        if self._open is False:
            print 'Error. No journal entry currently open.'
            return
        field = self._glossary[field_title]
        field_value = field.input()
        if field_value == 'escape':
            raise UserEscape('Abandoning new entry creation')
        key = field.key(field_value)
        self._current_list.append(key)
    def close(self, abandon=False):
        if not abandon:
            self.write(self._current_list, self._current_dictionary)
        self._current_list = []
        self._current_dictionary = {}
        self.reset_filter()
    def save(self):
        filename = self._place + self.title + '.p'
        pickle.dump(self._records, open(filename, 'w'))
    def reset_filter(self):
        self._filtered = self._records.keys()
    def display(self):
        for t in sorted(self._filtered):
            l, d = self._records[t]
            self._show(l, d)
    def filter_on(self, field_title=None):
        if field_title == None:
            field_title = auto_input('Field on which to filter (<tab> for options): '
                                     , self._glossary)
        field = self._glossary[field_title]
        coded_values = []
        done = False
        while not done:
            coded_values.append(field.key(field.input()))
            q = raw_input('Include any other ' + field._handle_attribute + '\'s (y/[n])? ')
            if q != 'y':
                done = True
        self._filter_on(coded_values)
    def _filter_on(self, coded_values):
        times = []
        for t in self._filtered:
            l, d = self._records[t]
            if set(l).intersection(set(coded_values)) != set():
                times.append(t)
        self._filtered = times
    def __repr__(self):
        for key in self._records:
            l, d = self._records[key]
            self._show(l,d)
        return ''
    def times(self):
        return self._records.keys()
#        return self.title
    def test(self):
        print 'title=', self.title
        print '_fields=', self._fields
        print '_records:'
        for i in self._records:
            print i, ': ', self._records[i]
    def del_last(self, number=1):
        times = sorted(self._records.keys())
        last_times = times[-number:]
        for t in last_times:
            del self._records[t]
        self.reset_filter()


def parse_instruction():
    if 'libedit' in readline.__doc__:
       return "bind ^I rl_complete"
    else:
        return "tab: complete"
    
def auto_input(query, options):
    '''
    Print query and offer autocompletion on the options provided. Returns the supplied input
    '''
    def complete(text, state):
        for option in options:
            if option.startswith(text):
                if not state:
                    return option
                else:
                    state -= 1
    readline.parse_and_bind(parse_instruction())
    readline.set_completer(complete)
    valid_input = False
    while not valid_input:
        ret = raw_input(query)
        if ret not in options:
            print 'Invalid input. '
        else:
            valid_input = True
    return ret

def show(d):
    if type(d)==type({}):
        lengths = map(lambda x: len(str(x)), d.values())
        if len(lengths) != 0:
            maxlength = max(lengths)
        else:
            return
        for key in d:
            space = ''
            for i in range(maxlength - len(str(d[key]))):
                space += ' '
            s = str(d[key]) + space + ' (' + str(key) + ')'
            print s

def print_attributes(object):
    d = object.__dict__
    for k in d:
        print str(k) + ' = ' + str(d[k])

def prefix(s):
    return s.split('_')[0]

def dict_input(keys):
    d = {}
    for k in keys:
        d[k] = raw_input(k + ': ')
        if d[k] == 'escape':
            raise UserEscape('Abandoning dictionary input')
    return d






# testing
# stud = Field('student', place='fields/', handle='upi')
# cour = Field('course', place='fields/', handle='id')
# acti = Field('activity', place = 'fields/', handle='name')
# seme = Field('semester', place = 'fields/', handle='name')
# week = Field('week', place='fields/', handle='number')
# prov = Field('provider', place='fields/', handle='name')
# j = Journal('testlog', place='fields/', fields=[acti, stud, cour, seme, week, prov])

# stud.add('123456')
# stud['123456']['name']='anthony'
