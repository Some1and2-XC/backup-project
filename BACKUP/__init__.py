#!/usr/bin/env python3

"""
Author : Mark Tobin
Date   : Sept 21 2022

Backs up Files with the *.88 format
"""

import json
from shutil import copy2 as cp
from os import path
from os import sep as PathSep

def StoreSearch88():
    """Function for searching for Storage Devices
    Searches for devices with a @source.88 & @reference.88

    Requires installation of wmi
    Will Move Directories if used
    Reference: https://stackoverflow.com/a/61168723
    """

    from wmi import WMI
    from os import chdir
    from glob import glob
    from re import findall as match

    FoundPaths = {}
    for drive in WMI().Win32_LogicalDisk():
        chdir(drive.Caption)
        directory = glob("*.88")
        if "@reference.88" in directory:
            with open("@reference.88", "r") as file:
                FoundPaths["Reference"] = path.join(drive.Caption, match(r"(?<=@).*(?=@)", file.read())[0])
                file.close()
        if "@source.88" in directory:
            FoundPaths["Source"] = drive.Caption
    try:
        return (FoundPaths["Source"], FoundPaths["Reference"])
    except KeyError: return False
    except Exception as e:
        print("Unknown Error")
        return False

def create88(SourcePath: str = None, ReferencePath: str = None):
    """Main function of program

    # Notes
     - Maybe Make the absolute path not included so that reconstruction can happen within a folder instead of a in an entire filesystem
    """

    from os import getcwd, chdir
    from os import remove as rm
    from glob import glob
    from re import findall
    from hashlib import sha1
    from collections import namedtuple

    from functools import wraps

    def WOutput(OutputStr: str = None):
        """Function Wrapper for Writing Outputs

        Keyword arguments:
        OutputStr -- String printed on output (default None)
        """
        global OutputNumber
        OutputNumber = 0 # Number that gets printed on Command Initialisation
        if not isinstance(OutputStr, str):
            raise TypeError(f"Output Must be `str`, not {type(OutputStr)}")

        def OuterWrapper(func):
            @wraps(func)
            def InnerWrapper(*args, **kwargs):
                global OutputNumber
                print(f"Process [{OutputNumber}] | {OutputStr}" + " " * 15)
                # print(f"Process [{OutputNumber}] | {OutputStr}" + " " * 15, end="\r")
                OutputNumber += 1
                return func(*args, **kwargs)
            return InnerWrapper
        return OuterWrapper

    @WOutput("Starting Recursive Folder Search")
    def RecursiveSearch():
        """Function for finding all the files within a subfolder
        Gets a list of all the filenames at exist in a subfolder

        Keyword arguments:
        dir -- List of the Directory that is being dug (default list)
        """

        def DirectoryCarve(dir: list = []):
            if len(dir) != 0:
                chdir(dir[-1])
            subfolders = set()
            NewFiles = []
            for subfolder in glob("*/"):
                try:
                    LocalSubfolder = findall(r"[a-zA-Z0-9_.&#$@!%^&*’ \'\"\-\\\,\{\}\+\(\)\-\[\]]+(?=\\)" , subfolder)[0]
                    NewFiles = [*NewFiles, *DirectoryCarve(dir = [*dir, LocalSubfolder])]
                    subfolders.add(LocalSubfolder)
                except Exception as e:
                    print(f"Error on {subfolder}{dir} | {e}")
            files = set(glob("*")) - subfolders
            dir = PathSep.join(dir)
            chdir("..")
            return [
                *NewFiles,
                *[
                    (
                        ListEntry(file, dir)
                    ) for file in files 
                ]
            ]

        return DirectoryCarve()

    @WOutput("SHA1 of All Files")
    def MakeDictWithHashKey(SearchData):
        """Function for making every entry returned from `RecursiveSearch()` to dict with sha hash
        returns dict with file paths stored in list under dictionary with hash of the files as keys

        Keyword arguments:
        SearchData -- Takes the List output from `RecursiveSearch()` and takes hash of every File
        """
        def GetFileHash(filename):
            """Function for getting the Hash of every File
            Reference: https://www.semicolonworld.com/tutorial/python-find-hash-of-file
            Returns a sha1 has of filename passed
            """
            h = sha1() # Sets `h` to a `sha1()` object
            with open(filename, "rb") as file: # Opens file
                # Reads 1024 Chunks of the file until the end of the file (where chunk == b"")
                chunk = 0
                while chunk != b"":
                    chunk = file.read(1024)
                    h.update(chunk)
            return h.hexdigest()

        entries = {}

        SearchDataAmnt = len(SearchData)

        for i in range(SearchDataAmnt):
            entry = SearchData[i]
            print(f" - Hash : [{100 * (i + 1) / SearchDataAmnt:.2f}% : {i + 1} / {SearchDataAmnt}]" + " " * 15, end="\r")
            try:
                chdir(path.join(BasePath, entry.path))
                FileHash = GetFileHash(entry.filename)
                if FileHash not in entries:
                    entries[FileHash] = []
                entries[FileHash].append(path.join(entry.path, entry.filename))
            except PermissionError:
                """
                Catches errors caused by files not being readable by the current user / python
                """
                pass
        print()
        chdir(BasePath)
        return entries

    @WOutput("Copying Files")
    def XReferenceAndCopy(TreeDict):
        """Cross Reference and Copy all files
        """
        
        chdir(ReferencePath)

        CurrentFiles = [ i.split(".")[0] for i in glob(f"*{ext}") ] # Set of the files in the backup drives backup directory
        CurrentFiles = set(CurrentFiles)
        DirectoryFiles = set(TreeDict) # Gets `set()` type object of all the keys in TreeDict
        AddFiles = list(DirectoryFiles - CurrentFiles) # Gets list of all the files from the file that need to be added and removes the files that allready exist
        DeletionFiles = CurrentFiles - DirectoryFiles

        for file in DeletionFiles:
            # Deletes all the Files that exist in the CurrentFiles `set()` but not in the new dict
            try: rm(file)
            except: pass

        AddFileAmnt = len(AddFiles) # The total amount of files to add

        for i in range(AddFileAmnt):
            file = AddFiles[i]
            print(f" - File Copy : [{100 * (i + 1) / AddFileAmnt:.2f}% : {i + 1} / {AddFileAmnt}]" + " " * 15, end="\r")
            try:
                Source = TreeDict[file][0]
                Destination = file + ext
                cp(path.join(BasePath, Source), Destination)
            except Exception as e:
                print(f"\nError: {e}")
        print()

        with open(OutFileName + ext, "w") as f:
            f.write(json.dumps(TreeDict, sort_keys = True))
            f.close()

        return 1

    chdir(SourcePath)

    ListEntry = namedtuple("FilePaths", "filename path")
    BasePath = getcwd()
    ProjTree = RecursiveSearch()
    TreeDict = MakeDictWithHashKey(ProjTree)
    assert XReferenceAndCopy(TreeDict)

    print("\n\tBackup Completed!\n")

def regen88(ReferencePath: str = None):
    """Function for regenerating an 88

    Keyword arguments:
    OutputStr -- String printed on output (default None)
    """

    from os import getcwd
    from os import mkdir, chdir

    def RecursFolderGen(CurrentPath):
        """Generates Folder Recursively
        """

        if isinstance(CurrentPath, str):
            CurrentPath = path.normpath(CurrentPath) # Normalizes the path to the OSs perfered seperator
            CurrentPath = [ BaseFolder, *CurrentPath.split(PathSep) ][:-1] # Then splits it into sections based on that seperator

        try: mkdir(CurrentPath[0])
        except FileExistsError: pass
        except FileNotFoundError: return RecursFolderGen(CurrentPath[1::])
        except IndexError: return
        chdir(CurrentPath[0])
        RecursFolderGen(CurrentPath[1::])
        return True

    if ReferencePath: chdir(ReferencePath)

    BaseBase = getcwd()
    BaseFolder = "RESTOREDBACKUP"

    print("Starting Restore", end = "\r")

    with open(OutFileName + ext, "r") as file:
        data = json.loads(file.read())
        file.close()

    for key in data:
        for file in data[key]:
            RecursFolderGen(file)
            chdir(BaseBase)
            cp(key + ext, path.join(BaseFolder, file)) # Copies Files and uses some goofy syntax to remove the folder ending

    print("Finished Restore")

ext = ".88" # Extention for the filename
OutFileName = "@reconstruct" # The Filename of the reconstruction file
