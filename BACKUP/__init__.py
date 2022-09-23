#!/usr/bin/env python3

"""
Author : Mark Tobin
Date   : Sept 21 2022

Backs up Files with the *.88 format
"""

import json
from shutil import copy2 as cp

def create88():
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
        if not isinstance(OutputStr, str):
            raise TypeError(f"Output Must be `str`, not {type(OutputStr)}")

        def OuterWrapper(func):
            @wraps(func)
            def InnerWrapper(*args, **kwargs):
                global OutputNumber
                print(f"Process [{OutputNumber}] | {OutputStr}" + " " * 15, end="\r")
                t = func(*args, **kwargs)
                OutputNumber += 1
                return t
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
                    subfolder = findall(r"[a-zA-Z0-9_.& \-\\\,\{\}\+\(\)\-\[\]]+(?=\\)", subfolder)[0]
                    NewFiles = [*NewFiles, *DirectoryCarve(dir = [*dir, subfolder])]
                    subfolders.add(subfolder)
                except Exception as e:
                    print(f"Error on {subfolder}{dir} | {e}")
            files = set(glob("*")) - subfolders
            dir = "\\".join(dir)
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

    @WOutput("Converting Data Format")
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
        for entry in SearchData:
            try:
                chdir(f"{BasePath}\\{entry.path}")
                FileHash = GetFileHash(entry.filename)
                if FileHash not in entries:
                    entries[FileHash] = []
                entries[FileHash].append(f"{entry.path}\\{entry.filename}")
            except PermissionError:
                """
                Catches errors caused by files not being readable by the current user / python
                """
                pass
        chdir(BasePath)
        return entries

    @WOutput("Copying Files")
    def XReferenceAndCopy(TreeDict):
        """Cross Reference and Copy all files
        """
        
        chdir(ReferencePath)

        CurrentFiles = [ i.split(".")[0] for i in glob(f"*{ext}") ]
        CurrentFiles = set(CurrentFiles)
        DirectoryFiles = set(TreeDict) # Gets `set()` type object of all the keys in TreeDict
        AddFiles = CurrentFiles & DirectoryFiles
        DeletionFiles = CurrentFiles - DirectoryFiles

        for file in DeletionFiles:
            # Deletes all the Files that exist in the CurrentFiles `set()` but not in the new dict
            rm(file)

        for file in TreeDict:
            Source = TreeDict[file][0]
            Destination = file + ext
            cp(f"{BasePath}\\{Source}", Destination)

        with open(OutFileName + ext, "w") as f:
            f.write(json.dumps(TreeDict, sort_keys = True))
            f.close()

        return 1

    SourcePath = "C:\\Users\\User\\Desktop\\.py\\Fractals\\Kyros"
    ReferencePath = "C:\\Users\\User\\Desktop\\.py\\Backup Proj\\BACKUP\\BKF"

    chdir(SourcePath)

    ListEntry = namedtuple("FilePaths", "filename path")
    BasePath = getcwd()
    ProjTree = RecursiveSearch()
    TreeDict = MakeDictWithHashKey(ProjTree)
    assert XReferenceAndCopy(TreeDict)

    print("\n\n\tBackup Completed!\n")

def regen88():
    """Function for regenerating an 88

    Keyword arguments:
    OutputStr -- String printed on output (default None)
    """

    from os import getcwd
    from os import mkdir, chdir

    def RecursFolderGen(path):
        """Generates Folder Recursively
        """

        if isinstance(path, str):
            path = [ BaseFolder, *path.split("\\")[:-1] ]
        try: mkdir(path[0])
        except FileExistsError: pass
        except FileNotFoundError: return RecursFolderGen(path[1::])
        except IndexError: return
        chdir(path[0])
        RecursFolderGen(path[1::])
        return True

    BaseBase = getcwd()
    BaseFolder = "FD"

    with open(OutFileName + ext, "r") as file:
        data = json.loads(file.read())
        file.close()

    for key in data:
        for file in data[key]:
            RecursFolderGen(file)
            chdir(BaseBase)
            cp(key + ext, f"{BaseFolder}\\{file}")

OutputNumber = 0 # Number that gets printed on Command Initialisation

ext = ".88"
OutFileName = "..reconstruction"

if __name__ == "__main__":
    create88()
    regen88()
