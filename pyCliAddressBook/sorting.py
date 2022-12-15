"""
Sorting files to categorical folders.
Normalising names of files & folders.
Remoting empty folders.
Unpacking archives.
"""

from itertools import chain

import os
from pathlib import Path
import re
from shutil import move, unpack_archive
from typing import List


files_extension_to_folders = {
    'images': ['.jpeg', '.png', '.jpg', '.svg', '.bmp', '.tiff'],
    'video': ['.avi', '.mp4', '.mov', '.mkv', '.flv'],
    'documents': ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', '.djvu', '.djv', '.csv', '.fb2'],
    'audio': ['.mp3', '.ogg', '.wav', '.amr'],
    'archives': ['.zip', '.gz', '.tar']
    }

cyrillic_symbols = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюяёъыэ'
cyrillic_to_latin = ('a', 'b', 'v', 'h', 'g', 'd', 'e', 'ye',
                     'zh', 'z', 'y', 'i', 'yi', 'y', 'k', 'l',
                     'm', 'n', 'o', 'p', 'r', 's', 't', 'u',
                     'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'yu',
                     'ya', 'yo', '', 'y', 'e')
transliteration = {}

for cyrillic, latin in zip(cyrillic_symbols, cyrillic_to_latin):
    transliteration[ord(cyrillic)] = latin
    transliteration[ord(cyrillic.upper())] = latin.upper()

empty_folders = []
folders_to_rename = []


def find_files(path: Path) -> None:
    """
    Recursive searching files for sorting
    :param path: Path
        selected folder for sorting
    :return: None
    """
    for i in path.iterdir():

        if i.is_file():

            if (ext := i.suffix) in chain(*files_extension_to_folders.values()):

                new_name = normalize(i.stem)

                if ext in files_extension_to_folders['images']:
                    move_file(i, new_name, ext, 'images')

                elif ext in files_extension_to_folders['video']:
                    move_file(i, new_name, ext, 'video')

                elif ext in files_extension_to_folders['documents']:
                    move_file(i, new_name, ext, 'documents')

                elif ext in files_extension_to_folders['audio']:
                    move_file(i, new_name, ext, 'audio')

                elif ext in files_extension_to_folders['archives']:
                    unpack_archive_file(i, new_name, ext, 'archives')

        elif i.is_dir() and not (i.name in files_extension_to_folders):

            if not os.listdir(i):
                empty_folders.append(i)
            else:
                folders_to_rename.append(i)

            find_files(i)


def move_file(old_file_path: Path, new_name: str, ext: str, folder: str) -> None:
    """
    Moving normalized files to categorical folders
    :param old_file_path: Path
        old file location
    :param new_name: str
        normalized file name
    :param ext: str
        file extension
    :param folder: str
        categorical folder name
    :return: None
    """
    new_path_file = Path(old_file_path.parent, folder)
    new_path_file.mkdir(exist_ok=True, parents=True)
    new_path = (Path(old_file_path.parent, f'{new_name}{ext}'))
    os.rename(old_file_path, new_path)
    move(new_path, new_path_file)


def unpack_archive_file(old_file_path: Path, new_name: str, ext: str, folder: str) -> None:
    """
    Working with archives.
    Moving archives to the folder 'archives' and unpacking they there
    :param old_file_path: Path
        archive location
    :param new_name: str
        folder name of unpacking archive
    :param ext: str
        archive extension
    :param folder: str
        collective folder for unpacking archives, 'archives' by default
    :return: None
    """
    new_path_file = Path(old_file_path.parent, folder)
    new_path_file.mkdir(exist_ok=True, parents=True)
    new_path = (Path(old_file_path.parent, f'{new_name}{ext}'))
    os.rename(old_file_path, new_path)
    unpack_archive(new_path, Path(new_path_file, new_name), ext.replace('.', ''))
    os.remove(new_path)


def normalize(old_name: str) -> str:
    """
    Normalizing files' & folders' names.
    Translating cyrillic symbols to latin ones.
    Amending unacceptable symbols to '_' symbol.
    :param old_name: str
        folder/file's name before normalizing
    :return new_name: str
        folder/file's name after normalizing
    """
    new_name = old_name.translate(transliteration)
    new_name = re.sub(r'\W', '_', new_name)

    return new_name


def remove_empty_folders(folders: List[Path]) -> None:
    """
    Removing empty folders
    :param folders: list
        list of empty folder in sorting folder
    :return: None
    """
    for folder in folders:
        folder.rmdir()

    global empty_folders
    empty_folders = []


def rename_folders(list_folders: List[Path]) -> None:
    """
    Renaming folders
    :param list_folders: list
        folder list for normalizing
    :return: None
    """
    for folder in list_folders[::-1]:
        new_folder_name = normalize(folder.name)
        new_path_folder = (Path(folder.parent, f'{new_folder_name}'))
        try:
            os.rename(folder, new_path_folder)
        except FileExistsError:
            new_path_folder = (Path(folder.parent, f'{new_folder_name}_1'))
            os.rename(folder, new_path_folder)

    global folders_to_rename
    folders_to_rename = []


def perform() -> None:
    """
    Sorting files to categorical folders. Normalising names of files & folders.
    Remoting empty folders. Unpacking archives.
    """

    while True:
        sorting_folder = input('Enter folder for sorting: ')

        if not sorting_folder:
            path = Path().cwd()
        else:
            if not Path(sorting_folder).exists():
                print("Folder isn't exist")
                continue
            else:
                path = Path(sorting_folder)
        break

    find_files(path)
    remove_empty_folders(empty_folders)
    rename_folders(folders_to_rename)
    print('sorting is complete')


if __name__ == '__main__':
    perform()
