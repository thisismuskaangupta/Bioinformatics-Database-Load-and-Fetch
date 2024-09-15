# Bioinformatics-Database-Load-and-Fetch
this contains the code written for the MSc Bioinformatics course - Programming and Databases for Biologists. grade: A1:22

the task was to implement a bioinformatics database load and fetch utility.
note - all filenames were hardcoded because everything from the database architecture to the file parsing and queries were tailored to this particular dataset. all input files and scripts need to be in the same directory for the (main) script to run (except _methodsandclasses.py_, which may be on path.)

Usage - 
python \<program\>.py [–-createdb] [–-loaddb] [–-querydb=n] \<SQLite database file\>
  1. The –-createdb option should be used to create the database structure.
  2. The –-loaddb option should be used to parse the data files and insert the relevant data into the database. 
  3. The –-querydb option should be used to run one of the queries specified below on the created and loaded database. The argument n is a number from 1 to 9.

Inputs (provided) - 
A subset of complex multi-omics data from the following paper: Ahadi, S., Zhou, W., Schüssler-Fiorenza Rose, S.M. et al. Personal aging markers and ageotypes revealed by deep longitudinal profiling. Nat Med 26, 83–90 (2020). https://doi.org/10.1038/s41591-019-0719-5

The data consists of a mixture of preprocessed files produced from the measurements of the transcripts, proteins, and metabolites of a cohort of 106 individuals in the study. The structure of the data files is as follows.
1) _Subject.csv_ holds information on the 106 subjects of the study.
2) Subjects performed multiple visits where their multi-omics samples were taken. _HMP_transcriptome_abundance.tsv_, _HMP_proteome_abundance.tsv_, _HMP_metabolome_abundance.tsv_ are tab-separated files that contain the measurements of transcriptomics, proteomics and metabolomics (peaks) of the different samples from the subjects.

Queries -   
  1. Retrieve SubjectID and Age of subjects whose age is greater than 70.
  2. Retrieve all female SubjectID who have a healthy BMI (18.5 to 24.9). Sort the results in descending order.
  3. Retrieve the Visit IDs of Subject 'ZNQOVZV'. 
  4. Retrieve distinct SubjectIDs who have metabolomics samples and are insulin-resistant.
  5. Retrieve the unique KEGG IDs that have been annotated for the following peaks: 
    a. 'nHILIC_121.0505_3.5'
    b. 'nHILIC_130.0872_6.3'
    c. 'nHILIC_133.0506_2.3'
    d. 'nHILIC_133.0506_4.4'
  6. Retrieve the minimum, maximum and average age of Subjects.
  7. Retrieve the list of pathways from the annotation data, and the count of how many times each pathway has been annotated. Display only pathways that have a count of at least 10. Order the results by the number of annotations in descending order.
  8. Retrieve the maximum abundance of the transcript 'A1BG' for subject 'ZOZOW1T' across all samples.
  9. Retrieve the subjects’ age and BMI. If there are NULL values in the Age or BMI columns, that subject should be omitted from the results. At the same time, generate a scatter plot of age vs BMI using the query results and store the resulting scatter plot as a PNG image file called ‘age_bmi_scatterplot.png’ in the same directory as the program.

Approach to the Assignment - 
1) the data was understood and an entity-relationship diagram (ERD) was drawn to plan a database structure. (this is provided at the end of this README.)
2) this was implemented by SQL methods.
3) the above queries were coded.

![ERD](https://github.com/user-attachments/assets/7aec4592-f539-4f4c-908f-b323fd291c05)
