#setting up logging.
import logging
#getting the logger
logger = logging.getLogger('logger')
#setting the level of the logger
logger.setLevel(logging.WARNING)
#creating a stream handler.
shandler = logging.StreamHandler()
#formatting the stream handler
shandler.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - {%(pathname)s:%(lineno)d} - %(message)s'))
#adding the stream handler to the logger.
logger.addHandler(shandler)

#this function takes a line of the subject file in list format and 'cleans' the data, ie it converts the NA, unknown and Unknown entries into python NoneType, and converts the age and BMI columns into floats.
def subject_parser(input_list):
    for index, item in enumerate(input_list):
        if item == 'NA' or item == 'unknown' or item == 'Unknown':
            input_list[index] = None 
            #here, the NA, unknown, and Unknown entires are being converted to python NoneType, which will get converted into sql Null when being inserted into the database.
    
    #columns 3 and 4 in the input file (zero indexed) are age and BMI respectively, these need to be floats (or NoneType) in python so they're inserted into the database correctly, where the constraint DECIMAL exists for these values.
    if input_list[3] != None:
        input_list[3]=float(input_list[3])
    if input_list[4] != None:    
        input_list[4]=float(input_list[4])
    #if the input data for these indexes are not numbers, e.g. 'jane', then this should throw a value error. error handling for the same is added in the main program script.
    
    return input_list

#test suite
#this checks that the subject_parser function is cleaning data appropriately. 
#in the case that it isn't, the error is logged.
try:
    assert subject_parser(['ZMS5W76', 'unknown', 'F', '49.97', '32.73', '224', 'IR']) == ['ZMS5W76', None, 'F', 49.97, 32.73, '224', 'IR']
    assert type(subject_parser(['ZMS5W76', 'unknown', 'F', '49.97', '32.73', '224', 'IR'])[3]) == float
    assert type(subject_parser(['ZMS5W76', 'unknown', 'F', '49.97', '32.73', '224', 'IR'])[4]) == float
    assert subject_parser(['ZMS5W76', 'unknown', 'F', 'NA', '32.73', '224', 'IR']) == ['ZMS5W76', None, 'F', None, 32.73, '224', 'IR']
    assert type(subject_parser(['ZMS5W76', 'unknown', 'F', 'NA', '32.73', '224', 'IR'])[4]) == float
    assert subject_parser(['ZMS5W76', 'unknown', 'F', 'NA', '32.73', '224', 'IR'])[3] is None
except AssertionError:
    logger.error(f"Hello, the subject_parser method is not working as expected, please check.\n")

#creating a function to parse the sampleIDs and return the subject ID and the visit ID in a list (in that order).
def sampleID_parser(sampleID): 
    sampleID = str(sampleID)
    output_list = sampleID.split('-')
    return output_list

#test suite
try:
    assert sampleID_parser('ZOZOW1T-01') == ['ZOZOW1T', '01']
    assert sampleID_parser('jane-doe') == ['jane','doe']
except AssertionError:
    logger.error(f"Hello, the sampleID_parser function is not working as expected, please check.\n")

#creating a function to parse the HMP_metabolome_annotation.csv file. as an argument, it takes a line of the input file in the list format.
#we want to clean the data in three ways: 1) multiple annotations for the same peak, eg. x|y should be split, 2) same annotations for multiple peaks e.g. x(2) must be cleaned, and 3) empty entries (''), NAs, unknowns, or Unknowns must be converted to python NoneType.
def met_annot_parser(input_list):
    #list indexes 0, 1, 2, 5 are the peakID, metabolite name, KEGG and Pathway respectively, we only clean these since this is the data we want to finally store in the database.
    peakID = input_list[0]
    Metabolite_Name = input_list[1]
    KEGG = input_list[2]
    Pathway = input_list[5]
    #error handling for the peakID not existing has been added in the main script.

    #output_list_of_lists will be the cleaned data ready to be inserted into the database. an empty list is created to store this. this will be a list of lists, where every sub-list is one instance of data ready to be stored in the database.
    output_list_of_lists = []
    
    if KEGG is None or KEGG in ['','NA','unknown','Unknown']: #if KEGG does not exist, it is converted to NoneType in python. if it does exist, then it is parsed.
        KEGG = None
    #if KEGG is associated with multiple peaks, then it will have a number associated with it. this should be removed.
    elif KEGG[-3:] in ['(1)','(2)','(3)','(4)','(5)']:
        KEGG = KEGG[:-3]
    
    #now, the KEGG has been cleaned in two ways, empty data has been converted to NoneType and the number is removed. now, if KEGG has multiple annotations separated by '|', we want to separate these.
    if KEGG is not None:
        KEGG_list = KEGG.split('|') #we create a list of each value in the KEGG string.
        #this list will be used to create the output.

    #the same logic is applied to clean the metabolite name data.
    if Metabolite_Name is None or Metabolite_Name in ['','NA','unknown','Unknown']: 
        Metabolite_Name = None
    
    elif Metabolite_Name[-3:] in ['(1)','(2)','(3)','(4)','(5)']:
        Metabolite_Name = Metabolite_Name[:-3]
    
    if Metabolite_Name is not None:
        Metabolite_Name_list = Metabolite_Name.split('|') #we create a list of each value in the KEGG string.
        #this list will be used to create the output.

    #we clean empty data in the pathway column as well.
    #it can be assumed that every entry in the pathway column is either empty or has one instance of data.
    if Pathway is None or Pathway in ['','NA','unknown','Unknown']: 
        Pathway = None

    #Now that we have individually parsed the metabolite name, KEGG and the Pathway, the output_list_of_lists can be created.
    #There are four possible cases here, that both metabolite name and KEGG are lists, that both are NoneType, and that one is a list and the other is a NoneType.
    
    #Case I - that both are lists
    #if metabolite name is a list containing multiple entries, e.g. ['name1','name2'] and KEGG is a list containing multiple entries, e.g. ['KEGG1','KEGG2'], then we want to store these in the database as separate instances, like so - instance one - ['PeakID','name1','KEGG1','Pathway'], and instance two - ['PeakID','name2','KEGG2','Pathway']. Our input list is formatted such that their indexes correspond, meaning the first value of metabolite name list should correspond to the first value in the KEGG list, so name1 corresponds to KEGG1 in the example, and so on. 
    #the function should return them in the following format - [['PeakID','name1','KEGG1','Pathway'],['PeakID','name2','KEGG2','Pathway']]
    if KEGG is not None and Metabolite_Name is not None:
        for number in range(0,len(KEGG_list),):
            output_list_of_lists.append([peakID,Metabolite_Name_list[number],KEGG_list[number],Pathway]) #this will iterate x number of times, where x is the number of items in the KEGG_list, which is the same as the metabolite name list. it is stored in the manner described in above example.

    #Case II - that both are NoneType
    elif KEGG is None and Metabolite_Name is None:
        output_list_of_lists.append([peakID,Metabolite_Name,KEGG,Pathway]) #if both are NoneType, then only one list may be created and stored.

    #Case III - that metabolite name is a list and KEGG is NoneType
    elif KEGG is None and Metabolite_Name is not None:
        for number in range(0,len(Metabolite_Name_list,)):
            output_list_of_lists.append([peakID,Metabolite_Name_list[number],KEGG,Pathway])
            #in this loop, where metabolite name may be ['name1','name2'], the resultant final list should be [['PeakID','name1',None,'Pathway'],['PeakID','name2',None,'Pathway']]

    #Case IV - that metabolite name is None and KEGG is a list (similar logic as Case III)
    elif KEGG is not None and Metabolite_Name is None:
        for number in range(0,len(KEGG_list),):
            output_list_of_lists.append([peakID,Metabolite_Name,KEGG_list[number],Pathway])

    #the output list is now ready to be inserted into the database. hence, the function has finished cleaning the data and preparing the output.
    return output_list_of_lists

#test suite
try:
    assert met_annot_parser(['nHILIC_103.0036_4', 'C3H4O4', '', '', '', '']) == [['nHILIC_103.0036_4','C3H4O4', None, None]]
    assert met_annot_parser(['examplepeakID', '', 'KEGG1|KEGG2|KEGG3', '', '', '']) == [['examplepeakID',None, 'KEGG1', None], ['examplepeakID',None, 'KEGG2', None], ['examplepeakID', None,'KEGG3', None]]
    assert met_annot_parser(['examplepeakID', '', 'KEGG1|KEGG2|KEGG3', '', '', 'unknown']) == [['examplepeakID', None,'KEGG1', None], ['examplepeakID', None,'KEGG2', None], ['examplepeakID', None,'KEGG3', None]]
    assert met_annot_parser(['examplepeakID', '', 'KEGG1|KEGG2|KEGG3', '', '', 'examplepathway']) == [['examplepeakID',None, 'KEGG1', 'examplepathway'], ['examplepeakID',None, 'KEGG2', 'examplepathway'], ['examplepeakID', None,'KEGG3', 'examplepathway']]
    assert met_annot_parser(['examplepeakID', '', '', '', '', 'examplepathway']) == [['examplepeakID',None, None, 'examplepathway']]
    assert met_annot_parser(['examplepeakID', 'name1|name2|name3(4)', 'KEGG1|KEGG2|KEGG3', '', '', 'examplepathway']) == [['examplepeakID','name1', 'KEGG1', 'examplepathway'], ['examplepeakID','name2', 'KEGG2', 'examplepathway'], ['examplepeakID', 'name3','KEGG3', 'examplepathway']]
    assert met_annot_parser(['examplepeakID', 'name1|name2|name3', '', '', '', 'examplepathway']) == [['examplepeakID','name1', None, 'examplepathway'], ['examplepeakID','name2', None, 'examplepathway'], ['examplepeakID', 'name3',None, 'examplepathway']]
except AssertionError:
    logger.error(f"Hello, the met_annot_parser function is not working as expected.")
#print("it worked!")


#this class takes the database file path as an argument and creates an object of the same.
#this contains two methods - query_db, which will be used to query the database, and insert_db, which will be used to insert values into the database.
import sqlite3
class DatabaseManager:

    #constructor
    def __init__(self, db_file):
        self.db_file = db_file
    
    #query_db method
    def query_db(self,select_statement: str,params=None):
        #constraint added - the select statement has to be a string, and parameters are optional.
        path = str(self.db_file)
        #a connection and cursor are created.
        connection = sqlite3.connect(path)        
        cur = connection.cursor()
        if params is None: #if there are no parameters, then only the select statement is executed.
            SELECTED_rows = cur.execute(select_statement).fetchall()
        else: #if parameters are passed, then these are used in the execute function.
            SELECTED_rows = cur.execute(select_statement,params).fetchall()
        cur.close()
        connection.close() #the connection and cursor are closed.
        return SELECTED_rows
        #this function takes the path to the database, the select statement to run on the database, and the parameters to run it on. it then returns a fetchall() list iterator.

    #insert_db method
    def insert_db(self,connection_name, cursor_name, insert_statement: str,params):
        #constraint added - the insert statement has to be a string
    
        error = False
        #while inserting the data, the database may throw an error, e.g. if that data has already been inserted into the database, or if any constraint has not been fulfilled (e.g. a null type has been supplied for a column with a NOT NULL or PRIMARY KEY constraint.)
        #this error has been handled as follows.
        try:
            cursor_name.execute(insert_statement,params)
        except Exception as e:
            error = True
            logger.error("Hello, there was an error in inserting the data. Here is the error message.")
            print(e)
        #if no error has been thrown, then the changes will be committed to the database file.
        if not error:
            connection_name.commit()
        
        #this function takes the path to the database, a connection, a cursor, the insert statement to run on the database, and the parameters to run it on. it then commits the change to the database, if there is no error.