-- Consolidated original schema plus the later README TEXT and ARRAY changes.
-- Fresh database only; original nullable columns and identifiers preserved.
-- Create Table Users
CREATE TABLE Users (
    UserID SERIAL,
    UserName VARCHAR(100) UNIQUE,
    Email VARCHAR(255) UNIQUE,
    Password VARCHAR(255),
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (UserID)
);

-- Create Table Person
CREATE TABLE Person (
    PersonID SERIAL,
    FirstName VARCHAR(100),
    Aliases VARCHAR(255)[],
    LastName VARCHAR(100),
    AssociatedUserID INTEGER,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (PersonID),
    FOREIGN KEY (AssociatedUserID) REFERENCES Users(UserID)
);

-- Create Table DocumentTags
CREATE TABLE DocumentTags (
    DocumentTagID SERIAL,
    DocumentTagDesc TEXT,
    AddedByUserID INTEGER NOT NULL,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,
    
    PRIMARY KEY (DocumentTagID),
    FOREIGN KEY (AddedByUserID) REFERENCES Users(UserID)
);
-- Create Table Documents
CREATE TABLE Documents (
    DocumentID SERIAL,
    LinkToDoc VARCHAR(255),
    DocumentDesc TEXT,
    OccurrenceDate DATE,
    AddedByUserID INTEGER NOT NULL,
    AssociatedPersonID INTEGER NOT NULL,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,
    
    PRIMARY KEY (DocumentID),    
    FOREIGN KEY (AddedByUserID) REFERENCES Users(UserID),
    FOREIGN KEY (AssociatedPersonID) REFERENCES Person(PersonID)
);

-- Create Table DocumentTagMapping
CREATE TABLE DocumentTagMapping (
    DocumentTagID INTEGER,
    DocumentID INTEGER,
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (DocumentTagID, DocumentID),
    FOREIGN KEY (DocumentTagID) REFERENCES DocumentTags(DocumentTagID),
    FOREIGN KEY (DocumentID) REFERENCES Documents(DocumentID)
);


-- Create Table RelationshipTypes
CREATE TABLE RelationshipTypes (
    RelationshipTypeID SERIAL, 
    RelationshipTypeDesc VARCHAR(255),
    CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (RelationshipTypeID)
);



-- Create Table Relations
CREATE TABLE Relations (
    PersonID INTEGER,
    DirectRelationship INTEGER,
    DirectRelationshipTypeID INTEGER,
    FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
    FOREIGN KEY (DirectRelationship) REFERENCES Person(PersonID),
    FOREIGN KEY (DirectRelationshipTypeID) REFERENCES 
    RelationshipTypes(RelationshipTypeID),
    PRIMARY KEY (PersonID, DirectRelationship)
);

Create table Lineages (
LineageID SERIAL PRIMARY KEY,
LineageName VARCHAR(255),
CreationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
IsActive BOOLEAN DEFAULT TRUE
);

CREATE TABLE LineagePersonConnector (
PersonID INTEGER not null,
LineageID INTEGER not null,
FOREIGN KEY (PersonID) REFERENCES Person(PersonID),
FOREIGN KEY (LineageID) REFERENCES Lineages(LineageID),
PRIMARY KEY (PersonID, LineageID)
);
