#!/usr/bin/env python
import readline
import cmd
import csv
import database as db
import time

data_path = 'data/'
auto_input = db.auto_input
detail = False

stud = db.Field('student', place=data_path, handle='upi')
cour = db.Field('course', place=data_path, handle='id')
acti = db.Field('activity', place = data_path, handle='name')
seme = db.Field('semester', place = data_path, handle='name')
week = db.Field('week', place=data_path, handle='number')
prov = db.Field('provider', place=data_path, handle='name')

print 'BARE BONES STUDENT DATABASE'
log_titles = ['TuakanaLog', 'PreenrolmentLog', 'Temp']
# comment out exactly one of the next two lines:
log_title = 'MyLog'
# log_title = auto_input('Log book: ', log_titles)
log = db.Journal(log_title, place=data_path, fields=[acti, stud, cour, week, seme, prov])

s = '2016 S2'
se=seme.key(s)
print 'The current semester is ' + s + '.'
q = raw_input('Type \'c\' to change, RETURN to continue: ')
if q == 'c':
    se = seme.key(seme.input())
current_semester = seme.lookup(se)
# restrict to current semester:
log._filter_on([se])

options = ['count', 'hours by week', 'hours by course', 'list', 'quit', 'new entry', 'discard', 'batch enrol', 'filter', 'find all', 'find student', 'detail on', 'detail off', 'import marks', 'import grades', 'add student', 'save', 'export emails', 'total hours', 'filter on ethnicity', 'filter on gender', 'generate report', 'mp']
def evaluate(d, key, replacement):
    ''' returns d[key] if key is a valid key. Otherwise returns replacement '''
    try:
        ret = d[key]
    except KeyError:
        ret = replacement
    return ret

def truncated(s, length):
    if len(s) > length:
        s = s[:length-3] + '...'
    else:
        n_spaces = length - len(s)
        for i in range(n_spaces):
            s = s + ' '
    return s

def lookup(t):
    '''
    Returns a triple (d1, d, student_record) of three dictionaries for the log entry log[t]:
       d1['activity'] ...  the activity (in words not code), d1['student'] is the student's upi, etc
       d ... the dictionary of event-specific data (eg d['mark out of 100'] =99 for an exam)
       student_record ... the dictionary of student attributes.
    '''
    l, d = log[t]
    ac, st, co, we, se, pr = l
    d1 = {}
    d1['activity'] = acti.lookup(ac)
    d1['student'] = stud.lookup(st)
    d1['course'] = cour.lookup(co)
    d1['week'] = week.lookup(we)
    d1['semester'] = seme.lookup(se)
    d1['provider'] = prov.lookup(pr)
    student_record = stud[stud.lookup(st)]
    return d1, d, student_record

def show_record(t):
    l, d = log[t]
    ac, st, co, we, se, pr = l
    ac = acti.lookup(ac)
    st = stud.lookup(st)
    co = cour.lookup(co)
    we = week.lookup(we)
    se = seme.lookup(se)
    pr = prov.lookup(pr)
    student_record = stud[st]
    if 'Last Name' not in student_record or 'First Name' not in student_record.keys():
        name = '- unknown - '
    else:    
        name = student_record['Last Name'] + ', ' + student_record['First Name']
    text = (time.ctime(t)[:16] + '  ' + st + '   ' + truncated(name, 20) + '  '
           + co + '     ' + we + '     ' + se   + '   ' + ac + '/' + pr)
    print text
    if len(d) != 0 and detail == True:
        for key in d:
            print '  ',
            print key + '=' + d[key],
        print ''

def count():
    n = len(log._filtered)
    print('The number of entries in the current filter is ' + str(n))

def for_jackson():
    with open('1on1.csv', 'w') as file:
         file = csv.writer(file)
         file.writerow(['Upi', 'Last Name', 'First Name', 'Ethnic Group',
                        'Course', 'Week', 'Duration (hrs)', 'Provider'])
         for t in log:
             d1, d, student_record = lookup(t)
             s = stud[d1['student']] # dictionary of student attributes
             e = evaluate(s, 'Ethnic Group', '')
             if d1['activity'] == 'one-on-one tutoring' and d1['semester'] == current_semester:
                 file.writerow([d1['student'], evaluate(s,'Last Name',''), evaluate(s,'First Name',''),
                               e, d1['course'], d1['week'], d['duration in hours'], d1['provider']])
    print 'Exported one-one-one tutoring details to \'1on1.csv\''

def add():
    try:
        log.open()
        log.add('student')
        upi = stud.lookup(log._current_list[-1])
        log.add('course')
        log.add('week')
        log._current_list.append(se)
        # Modify next line as appropriate:
        automatic_provider = False
        if automatic_provider:
            field = log._glossary['provider']
            key = field.key('Anthony Blaom')
            log._current_list.append(key)
        else:
            log.add('provider')            
        log.build()
        log.close()
        find(upi)
    except db.UserEscape:
        print 'Input cancelled.'
        print 'No new entry to log created.'
        log.close(abandon=True)

def find(upi=None):
    if upi == None:
        upi = stud.input()
    if upi == 'escape':
        print 'Input cancelled.'
        return
    coded_values = [stud.key(upi)]
    log.reset_filter()
    log._filter_on([se])
    log._filter_on(coded_values)
    s = stud[upi]
    print '------------------------------------------------------------------'
    u = '- unknown -'
    print evaluate(s, 'Last Name', u) + ', ' + evaluate(s,'First Name', u)
    print(evaluate(s, 'upi', u) + ' (upi)   ' + evaluate(s, 'Id', u) + ' (Id)   '
          + evaluate(s, 'Ethnic Group', u) + ' (Ethnic Group)   '
          + evaluate(s, 'Gender', u) + ' (Gender)  ' + evaluate(s, 'Acad Prog', u) + ' (Acad Program)')
    print evaluate(s, 'Address 1', u)
    print evaluate(s, 'Address 2', u)
    print evaluate(s, 'Address 3', u)
    a3 = evaluate(s, 'Address 3', u)
    a4 = evaluate(s, 'Address 4',u)
    if a3 != u:
        print a3
    if a4 != u:
        print a4
    print evaluate(s, 'City', u) + ', ' + evaluate(s, 'Postal', u)
    print evaluate(s, 'Country', u)
    show()

def filter():
    log.filter_on()
    show()

def filter_on_ethnicity():
    _new = []
    ethnicities = []
    done = False
    options = ['Maori', 'Pacific Islands', 'Other', 'done']    
    while not done:
        group = auto_input('Ethnic group (or \'done\' if finished): ', options)
        if group == 'done':
            done = True
        else:
            ethnicities.append(group)
    for t in log._filtered:
        l, d = log[t]
        ac, st, co, we, se, pr = l
        their_ethnicity = evaluate(stud[stud.lookup(st)],'Ethnic Group','Other')
        if their_ethnicity in ethnicities:
            _new.append(t)
    log._filtered=_new
    show()

def filter_on_gender():
    _new = []
    done = False
    options = ['M', 'F', 'Unknown']    
    gender = auto_input('Gender: ', options)
    for t in log._filtered:
        l, d = log[t]
        ac, st, co, we, se, pr = l
        their_gender = evaluate(stud[stud.lookup(st)],'Gender','Unknown')
        if their_gender == gender:
            _new.append(t)
    log._filtered=_new
    show()

def mp():
    '''
    This is a filter on ethnicity where the ethnicities are Maori and Pacific
    '''
    _new = []
    ethnicities = ['Maori', 'Pacific Islands']
    for t in log._filtered:
        l, d = log[t]
        ac, st, co, we, se, pr = l
        their_ethnicity = evaluate(stud[stud.lookup(st)],'Ethnic Group','Other')
        if their_ethnicity in ethnicities:
            _new.append(t)
    log._filtered=_new
    show()

def reset_filter():
    log.reset_filter()
    # only include current semester data:
    log._filter_on([se])
    show()

def show():
    print 'entry date        upi       Name                  Course  Week  Semester  Activity/Provider'
#    print '----------------------------------------------------------------------------------------------'
#    print '\n'
    for t in sorted(log._filtered):
        show_record(t)
    print 'entry date        upi       Name                  Course  Week  Semester  Activity/Provider'

def show_last():
    print 'entry date        upi       Name                  Course  Week  Semester  Activity/Provider'
#    print '----------------------------------------------------------------------------------------------'
    t = log.times()[-1]
    show_record(t)

def discard():
    log.del_last()
    print 'Last entry discarded.'

def batch_enrol():
    print('This function takes as input a CSV file whose first line is a header containing student' +
    ' attributes. One of these attributes must be \'Student Email\' (from which the student\'s' +
    ' upi is extracted). Another attribute must be \'Catalogue\' which is the Maths course number' +
    ' of a course the student is taking, with surrounding underscores;' +
    ' for example \'_102_\' is Maths 102. It is assumed that all fields not specific to the' +
    ' student have been removed, with the exception of \'Catalogue\'. E.g, \'Course Title\'' +
    ' and \'Subject\' should be removed. All students in the' +
    ' file are added to the current Bare Bones Student Log, attributes of existing students in the' +
    ' log are updated, and the student is enrolled in the given course in the week you will provide'
    '  below. ')
    ignored_attributes = ['Subject', 'Catalogue', 'Term', 'Course Title']
    filename = raw_input('CSV file: ')
    try:
        file = open(filename, 'rU') # the 'U' means various EOL characters are all understood
    except IOError:
        print 'Error. Unable to open \'' + filename + '\'.'
        return False
    csv_file = csv.reader(file)
    header = csv_file.next()
    we = week.key(week.input('Enter the week in which enrolments are being confirmed: '))
    pr = prov.key('Mathematics Department')
    
    if 'Student Email' not in header:
        print('Error. File does not appear to contain student emails.' +'No data read.' )
        ret = False
    else:
        for line in csv_file:
            record = {}
            for i in range(len(line)):
                record[header[i]]=line[i]
            upi = record['Student Email'].split('@')[0]
            stud.add(upi)
            # update the student database:
            for attribute in header:
                stud[upi][attribute]=record[attribute]
            # enrol student in the course for this record:
            log.open('confirmation of enrolment')
            st = stud.key(upi)
            course = stud[upi]['Catalogue'][1:4]
            co = cour.key(course)
            log._current_list.extend([st, co, we, se, pr])
            log._current_dictionary=dict()
            log.close()
            # delete fields not relevant to student record (course info):
            for attribute in ignored_attributes:
                if attribute in stud[upi].keys():
                    del stud[upi][attribute]
        stud._update_glossary()
        stud.save()
        print 'The student database has been updated and saved to file.'
        q = raw_input('Do you also want to save the updated log to file now ([y]/n)? ')
        if q != 'n':
            log.save()
        ret = True
    file.close()
    return ret

def import_marks():
    print('This function takes as input a CSV file whose first line is a header containing names of' +
    ' attributes. One of these attributes must be \'SIS Login ID\' and another must be \'Mark\'. ' +
    ' You will enter the assessment type, course number, the maximum mark, and week below.' +
    ' Only the marks of students' +
    ' already appearing in the current Bare Bones Student Log will be imported.')
    filename = raw_input('CSV file: ')
    try:
        file = open(filename, 'rU') # the 'U' means various EOL characters are all understood
    except IOError:
        print 'Error. Unable to open \'' + filename + '\'.'
        return False
    csv_file = csv.reader(file)
    header = csv_file.next()
    co = cour.key(cour.input())
    options = ['test', 'exam']
    activity = auto_input('Assessment type: ', options)
    max_mark = float(raw_input('Maximimum mark: '))
    we = week.key(week.input('Week in which the assessment occured: '))
    pr = prov.key('Mathematics Department')
    
    if 'SIS Login ID' not in header:
        print('Error. File does not appear to contain a field headed \'SIS Login ID\'.' +'No data read.' )
        ret = False
    else:
        for line in csv_file:
            record = {}
            for i in range(len(line)):
                record[header[i]]=line[i]
            upi = record['SIS Login ID']
            # add journal entry recording mark obtained:
            if upi in stud.handles():
                log.open(activity)
                st = stud.key(upi)
                log._current_list.extend([st, co, we, se, pr])
                d={}
                mark = record['Mark']
                if mark == '':
                    mark = '0'
                d['mark out of 100']=str(100.0*float(mark)/max_mark)
                log._current_dictionary=d
                log.close()
        print 'The marks have been successfully imported.'
        q = raw_input('Do you want to save the updated log to file now ([y]/n)? ')
        if q != 'n':
            log.save()
        ret = True
    file.close()
    reset_filter()
    return ret

def import_grades():
    print('This function takes as input a CSV file whose first line is a header containing names of' +
    ' attributes. One of these attributes must be \'SIS Login ID\' and another must be \'Final Grade\'. ' +
    ' You will enter the course number below.' +
    ' Only the grades of students' +
    ' already appearing in the current Bare Bones Student Log will be imported.')
    filename = raw_input('CSV file: ')
    try:
        file = open(filename, 'rU') # the 'U' means various EOL characters are all understood
    except IOError:
        print 'Error. Unable to open \'' + filename + '\'.'
        return False
    csv_file = csv.reader(file)
    header = csv_file.next()
    co = cour.key(cour.input())
    activity = 'final grade'
    we = week.key('e4')
    pr = prov.key('Mathematics Department')
    if 'SIS Login ID' not in header:
        print('Error. File does not appear to contain a field headed \'SIS Login ID\'.' +'No data read.' )
        ret = False
    else:
        for line in csv_file:
            record = {}
            for i in range(len(line)):
                record[header[i]]=line[i]
            upi = record['SIS Login ID']
            # add journal entry recording mark obtained:
            if upi in stud.handles():
                log.open(activity)
                st = stud.key(upi)
                log._current_list.extend([st, co, we, se, pr])
                d={}
                grade = evaluate(record, 'Final Grade', 'problem')
                if grade == 'problem':
                    print 'No column with header \'Final Grade\'.'
                    return False
                if grade == '':
                    grade = 'unknown'
                d['grade']=grade
                log._current_dictionary=d
                log.close()
        print 'The grades have been successfully imported.'
        q = raw_input('Do you want to save the updated log to file now ([y]/n)? ')
        if q != 'n':
            log.save()
        ret = True
    file.close()
    reset_filter()
    return ret

def export_emails():
    q = raw_input('Enter \'f\' to get emails in current filter, \'n\' for all NOT in current filter: ')
    filename = raw_input('File name for emails: ')
    emails = set()
    for t in log._records.keys():
        email = lookup(t)[0]['student'] + '@aucklanduni.ac.nz'
        if q == 'n':
            if t not in log._filtered:
                emails.add(email)
        else:
            if t in log._filtered:
                emails.add(email)
    with open(filename, 'w') as file:
        start = True
        for email in emails:
            if not start:
                file.write(',')
            start = False
            file.write(email)
    print('Emails succesfully exported to ' + filename)

def add_student():
    upi = raw_input('Upi of new student: ')
    if upi == 'escape':
        print 'Input cancelled'
        print 'No student added to database.'
        return
    stud.add(upi)
    first = raw_input('Student\'s first name: ')
    if first == 'escape':
        print 'Input cancelled'
        print 'No student added to database.'
        return
    stud[upi]['First Name'] = first
    last = raw_input('Student\'s last name: ')
    if last == 'escape':
        print 'Input cancelled'
        print 'No student added to database.'
        return
    stud[upi]['Last Name'] = last
    stud.save()
    print 'Student added and saved to file.'

def save():
    log.save()
    print 'The file for ' + log_title + ' has been updated.'

def total_hours():
    '''
    This routine looks at the current selection of journal entries (possibly
    reduced by calls to the filter routine) and totals the 'duration
    in hours' for entries that are 'one-on-one tuition'
    '''
    total = 0.0
    for t in log._filtered:
        d1, d, student_record = lookup(t)
        if d1['activity'] == 'one-on-one tutoring':
            dur = d['duration in hours']
            #hack to fix bad entries:
            if dur == '1 hr':
                dur = '1'
            total += float(dur)
    print('Based on the current selection of journal entries (as shown by \'list\')')
    print('the total number of hours given over to one-on-one tuition is: ' + str(total))

def hours_by_week():
    '''
    This routine looks at the current selection of journal entries (possibly
    reduced by calls to the filter routine) and totals the 'duration
    in hours' for entries that are 'one-on-one tuition' and breaks the result down by week
    '''
    print('Based on the current selection of journal entries (as shown by \'list\')')
    print('the number of hours given over to one-on-one tuition is: ')
    old_filter = log._filtered
    for i in week:
        we=week.key(i)
        log._filter_on([we])
        total = 0.0
        for t in log._filtered:
            d1, d, student_record = lookup(t)
            if d1['activity'] == 'one-on-one tutoring':
                dur = d['duration in hours']
                #hack to fix bad entries:
                if dur == '1 hr':
                    dur = '1'
                total += float(dur)
        print(week.lookup(we) + ': ' + str(total))
        log._filtered = old_filter
     
def hours_by_course():
    '''
    This routine looks at the current selection of journal entries (possibly
    reduced by calls to the filter routine) and totals the 'duration
    in hours' for entries that are 'one-on-one tuition' and breaks the result down by course
    '''
    print('Based on the current selection of journal entries (as shown by \'list\')')
    print('the number of hours given over to one-on-one tuition is: ')
    old_filter = log._filtered
    for i in cour:
        co=cour.key(i)
        log._filter_on([co])
        total = 0.0
        for t in log._filtered:
            d1, d, student_record = lookup(t)
            if d1['activity'] == 'one-on-one tutoring':
                dur = d['duration in hours']
                #hack to fix bad entries:
                if dur == '1 hr':
                    dur = '1'
                total += float(dur)
        print(cour.lookup(co) + ': ' + str(total))
        log._filtered = old_filter
     
def report():
    '''Generates a student-oriented report, based on the current filter (ie on
    journal entries generated by the command `list`). Only includes students 
    '''

    print 'Note that this report applies only to entries in the current filter. '
    include_all = raw_input('Include students not getting tuition (y/[n])? ')
    if include_all != 'y':
        include_all = 'n'
    
    # # force user to restrict to a single semester
    # print "Note that report applies only to current filter. Additionally,"
    # print "you must restrict to a particular semester." 
    # log.filter_on('semester')

    
    # get dictionary of tuition hours keyed on student upi's
    hours={}
    for t in log._filtered:
        d1, d, student_record = lookup(t)
        if d1['activity'] == 'one-on-one tutoring':
            student = d1['student']
            dur = d['duration in hours']
            #hack to fix bad entries:
            if dur == '1 hr':
                dur = '1'
            hrs = float(dur)
            if student not in hours.keys():
                hours[student] = hrs
            else:
                hours[student] += hrs

    # add the other students if required:
    if include_all == 'y':
        for t in log._filtered:
            d1, d, student_record = lookup(t)
            student = d1['student']
            if student not in hours.keys():
                hours[student]=0.0

    # Create dictionary <dd> of lists keyed on upis of students
    # getting tuition. Each list is of the form [UPI, Last Name, First
    # Name, Ethnic Group, Hours Tuition, dics], where `dics` is a list
    # of  course dictionaries, one for each course taken in the
    # selected semester.  A course dictionary is a dictionary with
    # exactly 3 possible keys: 'name', 'test' and 'grade', whose
    # corresponsing values are the course name, test mark and final
    # grade.
         
    dd = {}
    upis =  sorted(hours.keys())
    for upi in upis:
        s = stud[upi] # dictionary of student attributes
        last = evaluate(s,'Last Name','')
        first = evaluate(s,'First Name','')
        group = evaluate(s, 'Ethnic Group', '')
        record = [upi, last, first, group, hours[upi]]
        # record will be appended with the course dictionaries below

        # get set of courses
        courses = set()
        for t in log._filtered:
            d1, d, student_record = lookup(t)
            if d1['student'] == upi:
               if d1['activity'] in ['test', 'final grade']:
                    courses.add(d1['course'])

        # get test mark and grade for each course
        cd = {} # a dictionary of course dictionaries, keyed on course name
        for co in courses:
            cd[co]={'name':co, 'test':'', 'grade':''}
        for t in log._filtered:
             d1, d, student_record = lookup(t)
             if d1['student'] == upi:
                 co = d1['course']
                 if d1['activity'] == 'test':
                     cd[co]['test']=d['mark out of 100']
                 elif d1['activity'] == 'final grade':
                     cd[co]['grade']=d['grade']
                     
        # append the course dictionaries to the student's record
        for co in courses:
            record.append(cd[co])

        # put the student record in the master dictionary
        dd[upi]=record

    # write out the results to file
    print 'Report successfully generated.'
    filename = raw_input('Full name of file to contain report: ')
    with open(filename, 'w') as file:
        file = csv.writer(file)
        header = ['Upi', 'Last Name', 'First Name', 'Ethnic Group', 'Hours Tuition',
                  'Course1', 'Test1', 'Mark1', 'Course2', 'Test2', 'Mark2',
                  'Course3', 'Test3', 'Mark3', 'Course4', 'Test4', 'Mark4']
        file.writerow(header)
        print header
        for upi in sorted(dd.keys()):
            record = dd[upi]
            row = record[:5]
            record = record[5:]
            n_blank = 4 - len(dd)
            for cd in record:
                row.append(cd['name'])
                row.append(cd['test'])
                row.append(cd['grade'])
            for i in range(n_blank):
                row.extend(['','',''])
            file.writerow(row)
            print row

done = False
while not done:
    opt = auto_input(log_title + '> ', options)
    if opt == 'quit':
        q = raw_input('Save changes ([y]/n)? ')
        if q != 'n':
            log.save()
            print 'Logbook saved to disk.'
            for_jackson()
        done = True
    if opt == 'export one-on-one':
        for_jackson()
    elif opt == 'new entry':
        add()
    elif opt == 'list':
         show()
    elif opt == 'discard':
        discard()
    elif opt == 'batch enrol':
        if not batch_enrol():
            print 'Error. Batch enrolment failed.'
    elif opt == 'import marks':
        if not import_marks():
            print 'Error. Problem importing marks.'
    elif opt == 'import grades':
        if not import_grades():
            print 'Error. Problem importing grades.'
    elif opt == 'filter':
        filter()
    elif opt == 'find all':
        reset_filter()
    elif opt == 'list':
        show()
    elif opt == 'find student':
        find()
    elif opt == 'detail on':
        detail = True
    elif opt == 'detail off':
        detail = False
    elif opt == 'add student':
        add_student()
    elif opt == 'save':
        save()
    elif opt == 'export emails':
        export_emails()
    elif opt == 'generate report':
        report()
    elif opt == 'total hours':
        total_hours()
    elif opt == 'filter on ethnicity':
        filter_on_ethnicity()
    elif opt == 'filter on gender':
        filter_on_gender()
    elif opt == 'hours by week':
        hours_by_week()
    elif opt == 'hours by course':
        hours_by_course()
    elif opt == 'count':
        count()
    elif opt == 'mp':
        mp()



    
       


