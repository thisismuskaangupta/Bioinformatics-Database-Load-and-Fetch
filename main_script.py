#importing the required libraries
import sqlite3 #for sql wrapping
import methodsandclasses #my set of methods and classes used in this script.

#setting up logging.
import logging
#getting the logger
main_logger = logging.getLogger('main_logger') #since there is a logger in the imported 'methodsandclasses.py' script as well, these have to be named.
#setting the level of the logger
main_logger.setLevel(logging.WARNING)
#creating a stream handler.
shandler = logging.StreamHandler()
#formatting the stream handler
shandler.setFormatter(logging.Formatter('%(levelname)s - %(asctime)s - {%(pathname)s:%(lineno)d} - %(message)s'))
#adding the stream handler to the logger.
main_logger.addHandler(shandler)

#part 1 of the assignment - creating the database
#defining a function to create the database
def database_creator(given_database_path):
    connection = sqlite3.connect(given_database_path) #creating the connection
    cur = connection.cursor() #creating the cursor

    try:
        with open('sql_ddl.sql') as sqlfile:
            sql_script = sqlfile.read() #sql ddl script is read.
    except FileNotFoundError: #error is handled and program is stopped if the script is not found. 
        main_logger.error(f"Hello, the SQL DDL file (sql_ddl.sql) does not exist in the working directory, please check and run the script again.\n")
        raise SystemExit(1)

    try:
        cur.executescript(sql_script) #script is executed.
    except Exception as e:
        main_logger.error(f"Hello, the database could not be created, the following error was encountered. Please check and run the script again, raising SystemExit.\n{e}")
        raise SystemExit(1)

    connection.commit() #changes are committed to the database file.
    cur.close()
    connection.close() #the cursor and connection are closed.


#part 2 of the assignment - inserting the data.
#defining a function to load the database
def database_loader(given_database_path):
    import sqlite3

    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created so that methods from the DatabaseManager class may be used.
    connection = sqlite3.connect(given_database_path) #creating the connection
    cur = connection.cursor() #creating the cursor

    #inserting the subject data first.
    try:
        with open('Subject.csv','r') as in_file:
            next(in_file) #skipping the header line
            for line in in_file:
                line = line.rstrip().rsplit(',')
                #print(type(line))
                #break
                #this has created a list of the given line. this may now be cleaned using an imported function.
                try:
                    cleaned_line = methodsandclasses.subject_parser(line)
                #if there are any values in the age or BMI columns that are neither NoneType, nor numbers, then the function will throw a ValueError. (Details are in the methodsandclasses.py file.)
                except ValueError:
                    main_logger.warning(f"Hello, the following line in the Subject.csv file contains bad data, line has been skipped.\n")
                    print(line)
                    continue
                
                #we now have a variable called cleaned_line containing a list of the data from the input file. we will now reformat the chronology so only the essential data gets input into the database file, and in the right order (to maintain data integrity).
                #print(cleaned_line)
                #break
                
                #the order of columns in the database is subjectID, age, BMI, sex, and insulin_status. 
                list_to_input = [cleaned_line[0],cleaned_line[3],cleaned_line[4],cleaned_line[2],cleaned_line[6]]
                #print(list_to_input)
                #break
                sql = "INSERT INTO Subject VALUES (?,?,?,?,?);" #creating insert statement in sql
                #calling insert_db method from DatabaseManager class to insert the data.
                db.insert_db(connection,cur,sql,list_to_input)
    except FileNotFoundError:
        main_logger.error(f"Hello, the Subject.csv file was not found in the working directory, please check and run the script again.\n")


    #inserting the metabolome abundance and sample data now.
    try:
        with open('HMP_metabolome_abundance.tsv','r') as in_file:
            next(in_file)
            for line in in_file:
                line = line.rstrip().rsplit()
                #print(line)
                #break

                #we want to extract only the sample ID, as this is the information that will be stored in the Metabolome_Abundance and Sample tables.
                sampleID = line[0]
                #print(sampleID)
                #break

                #before parsing the sample ID, we want to check that it is in the expected format. if not, we skip the line it is in.
                if '-' in sampleID:
                    pass
                else:
                    main_logger.warning(f"Hello, the sample ID in the following line of data is not in the expected format, skipping this.\n{line}\nThe sample ID is {sampleID}.")
                    continue

                #now that we have filtered for the sampleID being in the expected format, we can parse it.
                subjectandvisitID_list = methodsandclasses.sampleID_parser(sampleID)

                #now that we have all the required input data, they can be formatted to be input correctly into the database file.
                #for both the Sample and Metabolome_Abundance tables, the order of the columns is SampleID, SubjectID, and VisitID.
                list_to_input = [sampleID,subjectandvisitID_list[0],subjectandvisitID_list[1]]
                #print(list_to_input)
                #break

                #creating insert statement 
                sql = "INSERT INTO Sample VALUES (?,?,?);"
                #calling insert_db method from DatabaseManager class to insert the data.
                db.insert_db(connection,cur,sql,list_to_input)

                #repeating this for the Metabolome_Abundance table
                sql = "INSERT INTO Metabolome_Abundance VALUES (?,?,?);"
                db.insert_db(connection,cur,sql,list_to_input)
    except FileNotFoundError: #catching the error in case the file is not found.
        main_logger.error(f"Hello, the HMP_metabolome_abundance.tsv file was not found in the working directory, please check and run the script again.\n")



    #inserting the samples table data from the proteome abundance file.
    #the logic for this is the same as that of the metabolome abundance file.
    try:
        with open('HMP_proteome_abundance.tsv','r') as in_file:
            next(in_file)
            for line in in_file:
                line = line.rstrip().rsplit()
                sampleID = line[0]
                if '-' in sampleID:
                    pass
                else:
                    main_logger.warning(f"Hello, the sample ID in the following line of data is not in the expected format, skipping this.\n{line}\nThe sample ID is {sampleID}.")
                    continue
                subjectandvisitID_list = methodsandclasses.sampleID_parser(sampleID)
                list_to_input = [sampleID,subjectandvisitID_list[0],subjectandvisitID_list[1]]
                sql = "INSERT INTO Sample VALUES (?,?,?);"
                db.insert_db(connection,cur,sql,list_to_input)
    except FileNotFoundError:
        main_logger.error(f"Hello, the HMP_proteome_abundance.tsv file was not found in the working directory; please check and run the script again.\n")



    #inserting the data from the HMP_transcriptome_abundance.tsv file into the Sample table and the Transcriptome_Abundance table.
    #the logic for this is the same as that of the HMP_metabolome_abundance.tsv file, with the small difference that there is an additional attribute in the Transcriptome_Abundance, ie the A1BG value.
    try:
        with open('HMP_transcriptome_abundance.tsv','r') as in_file:
            next(in_file)
            for line in in_file:
                line = line.rstrip().rsplit()
                sampleID = line[0]
                if '-' in sampleID:
                    pass
                else:
                    main_logger.warning(f"Hello, the sample ID in the following line of data is not in the expected format, skipping this.\n{line}\nThe sample ID is {sampleID}.")
                    continue
                subjectandvisitID_list = methodsandclasses.sampleID_parser(sampleID)
                
                #inputting Sample table values first.
                list_to_input = [sampleID,subjectandvisitID_list[0],subjectandvisitID_list[1]]
                sql = "INSERT INTO Sample VALUES (?,?,?);"
                db.insert_db(connection,cur,sql,list_to_input)

                #then inputting Transcriptome_Abundance table values.
                #line[1] contains the A1BG value, which is the last column in the database table.
                try:
                    A1BG = float(line[1]) #this data needs to be a float.
                except ValueError:
                    main_logger.warning(f"Hello, the A1BG data for the sample ID {sampleID} is not a number. Skipping this.\n")
                    continue
                list_to_input.append(A1BG) 
                sql = "INSERT INTO Transcriptome_Abundance VALUES (?,?,?,?);"
                db.insert_db(connection,cur,sql, list_to_input)

    except FileNotFoundError:
        main_logger.error(f"Hello, the HMP_transcriptome_abundance.tsv file was not found in the working directory, please check and run the script again.\n")



    #inserting the data from the HMP_metabolome_annotation.csv file into the Metabolome_Annotation table.
    try:
        with open('HMP_metabolome_annotation.csv','r') as in_file:
            next(in_file)
            for line in in_file:
                line = line.rstrip().rsplit(',')

                #line index 0, ie peakID cannot be null, since every instance of the data is related to at least one peak.
                if line[0] in ['','NA','unknown','Unknown']:
                    main_logger.warning(f"Hello, the following instance of data in the HMP_metabolome_annotation.csv file does not have a peak associated with it. Skipping this.\n{line}")
                    continue
                
                list_of_lists_to_input = methodsandclasses.met_annot_parser(line) #this function returns a list of lists, each of which is a separate instance of the data, ready to be input in the database. additional details in the methodsandclasses script.
                sql = 'INSERT INTO Metabolome_Annotation VALUES (?,?,?,?);'
                for each_list in list_of_lists_to_input:
                    db.insert_db(connection,cur,sql,each_list)

    except FileNotFoundError:
        main_logger.error(f"Hello, the HMP_metabolome_annotation.csv file was not found in the working directory. Please check and run the script again.\n")

    cur.close()
    connection.close()


#part 3 of the assignment, querying the database.
#defining a function for each query.

#query 1
def database_query_1(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = 'SELECT SubjectID, Age FROM Subject WHERE Age > 70;'
    query_result = db.query_db(sql) #this uses the query_db method from the DatabaseManager class.
    for instance in query_result:
        print(f"{instance[0]}\t{instance[1]}")



#query 2
def database_query_2(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) 
    sql = "SELECT SubjectID FROM Subject WHERE SEX = 'F' AND BMI BETWEEN 18.5 AND 24.9 ORDER BY BMI DESC;"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(instance[0])



#query 3
def database_query_3(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = "SELECT DISTINCT VisitID FROM Sample WHERE SubjectID = 'ZNQOVZV';"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(instance[0])



#query 4
def database_query_4(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = "SELECT DISTINCT Subject.SubjectID FROM Subject, Metabolome_Abundance WHERE Metabolome_Abundance.SubjectID = Subject.SubjectID AND Subject.Insulin_Status = 'IR';"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(instance[0])



#query 5
def database_query_5(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = "SELECT DISTINCT KEGG FROM Metabolome_Annotation WHERE PeakID IN ('nHILIC_121.0505_3.5','nHILIC_130.0872_6.3','nHILIC_133.0506_2.3','nHILIC_133.0506_4.4');"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(f"{instance[0]}")



#query 6
def database_query_6(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = "SELECT MIN(Age), MAX(Age), AVG(Age) FROM Subject;"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(f"{instance[0]}\t{instance[1]}\t{instance[2]}")



#query 7
def database_query_7(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = "SELECT Pathway, COUNT(*) FROM Metabolome_Annotation WHERE Pathway IS NOT NULL GROUP BY Pathway HAVING COUNT(*) > 9 ORDER BY COUNT(*) DESC;"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(f"{instance[0]}\t{instance[1]}")



#query 8
def database_query_8(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    sql = "SELECT MAX(A1BG) FROM Transcriptome_Abundance WHERE SubjectID = 'ZOZOW1T';"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(instance[0])



#query 9
def database_query_9(given_database_path):
    db = methodsandclasses.DatabaseManager(given_database_path) #the database object is created.
    
    #creating lists of data to use for plotting.
    x_axis_age = []
    y_axis_bmi = []

    sql = "SELECT Age, BMI FROM Subject WHERE Age IS NOT NULL AND BMI IS NOT NULL;"
    query_result = db.query_db(sql)
    for instance in query_result:
        print(f"{instance[0]}\t{instance[1]}")

        #while iterating through the results to print them, they're also added to the lists which will be used to create the plot.
        x_axis_age.append(instance[0])
        y_axis_bmi.append(instance[1])

    #creating the scatterplot and storing it
    import matplotlib.pyplot as plt

    #scatterplot is created.
    plt.scatter(x_axis_age,y_axis_bmi)

    #axes are labelled.
    plt.xlabel('Age')
    plt.ylabel('BMI')

    #plot is titled.
    plt.title('Query 9 Scatterplot')

    #plot is saved in the working directory.
    plt.savefig('age_bmi_scatterplot.png')

    #clearing the plot
    plt.clf()

#creating the command line
import argparse

#parser is created, containing the program name, description, epilog, and formatter.
parser = argparse.ArgumentParser(prog='CW2',description='this program creates a database based on given input files, loads the database, and queries it.',epilog='thanks and regards',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

#four arguments are added, three with flags (optional) (--createdb, --loaddb, and --querydb), and one positional (compulsory).
#--createdb and --loaddb are configured so that if they're called, their value is stored as 'True' (the boolean), and they do not take any argument.
parser.add_argument('--createdb', required=False, action='store_true',help='use this argument to create the database.')
parser.add_argument('--loaddb', required=False, action='store_true',help='use this argument to load the database. please ensure that all the required input files exist in the current working directory and have been named appropriately.')
#--querydb is configured so that it takes an int argument, and its default is false.
parser.add_argument('--querydb', type=int, required=False,default=False,help='use this argument to query the database, please specify the desired query number using --querydb=n format.')
#the positional argument that takes the file is compulsory.
parser.add_argument('positional_file_argument',help='please write the database filename in this argument. make sure that the file exists in the current working directory or that the full file address has been passed.')

#a list containing the arguments passed in the command line is created.
args = parser.parse_args()

database_path = str(args.positional_file_argument)

if args.createdb: #if --createdb is passed in the command line, the function is called to create the database.
    database_creator(database_path)
else: #if --createdb is not passed, it is expected that the given database file already exists. this is checked before executing any other arguments.
    try:
        with open(database_path):
            pass
    except FileNotFoundError:
        main_logger.error("Hello, the given database file does not exist in the current working directory. Please check and run the script again.")
        raise SystemExit(1)

if args.loaddb: #if the --loaddb argument is passed, the database is loaded.
    database_loader(database_path)

if args.querydb is not False: #the default value of --querydb argument has been set to the boolean False, if it is not false, it is assumed that an integer between 1 and 9 (inclusive) has been provided. in case the input is not an integer, argparse handles the error.
    #queries are run based on the integer that is provided.
    if args.querydb == 1:
        database_query_1(database_path)
    elif args.querydb == 2:
        database_query_2(database_path)
    elif args.querydb == 3:
        database_query_3(database_path)
    elif args.querydb == 4:
        database_query_4(database_path)
    elif args.querydb == 5:
        database_query_5(database_path)
    elif args.querydb == 6:
        database_query_6(database_path)
    elif args.querydb == 7:
        database_query_7(database_path)
    elif args.querydb == 8:
        database_query_8(database_path)
    elif args.querydb == 9:
        database_query_9(database_path)
    else:
        main_logger.error("Hello, the passed integer was not between 1 and 9 (inclusive).")
