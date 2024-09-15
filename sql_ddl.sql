--this is the DDL to create the database.

--creating subject entity's table 
CREATE TABLE Subject (
	SubjectID VARCHAR(250) NOT NULL,
	Age DECIMAL(13,10),
	BMI DECIMAL(13,10),
	SEX CHAR,
	Insulin_Status CHAR(2),
	PRIMARY KEY (SubjectID)
);

--creating the samples entity's table (this contains all the sample IDs and will be used to answer query 3)
--this is a weak entity
CREATE TABLE Sample (
	SampleID VARCHAR(250) NOT NULL,
	SubjectID VARCHAR(250) NOT NULL,
	VisitID VARCHAR(250) NOT NULL,
	FOREIGN KEY (SubjectID) REFERENCES Subject(SubjectID)
);

--creating the metabolome abundance entity's table 
CREATE TABLE Metabolome_Abundance (
	SampleID VARCHAR(250) NOT NULL,
	SubjectID VARCHAR(250) NOT NULL,
	VisitID VARCHAR(250) NOT NULL,
	PRIMARY KEY (SampleID),
	FOREIGN KEY (SubjectID) REFERENCES Subject(SubjectID)
);

--creating the transcriptome abundance entity's table 
CREATE TABLE Transcriptome_Abundance (
	SampleID VARCHAR(250) NOT NULL,
	SubjectID VARCHAR(250) NOT NULL,
	VisitID VARCHAR(250) NOT NULL,
	A1BG DECIMAL(50,25),
	PRIMARY KEY (SampleID),
	FOREIGN KEY (SubjectID) REFERENCES Subject(SubjectID)
);

--creating the metabolome annotation entity's table
--this is a weak entity 
CREATE TABLE Metabolome_Annotation (
	PeakID VARCHAR(250),
	KEGG VARCHAR(25),
	Pathway VARCHAR(500)
);