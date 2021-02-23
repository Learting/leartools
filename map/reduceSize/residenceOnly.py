#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Version 1.0
# Author: Learting


import math
import os
import re
import shutil
import sys


FILE_NAME_FORMAT = 'r.x.z.mca'  # 1.16 region files name format
REGION_SIZE = 512  # 1.16 region size
REGION_LOCATION = ['region', 'DIM-1/region', 'DIM1/region']
# overworld, nether, end


class ResidencesOnly:
    """
    Method 0

    Reduce the server's map size by saving region files containing
    residences registered in the Residence plugin only.
    """

    def __init__(self, residences_file_path, old_world_directory,
                 new_world_directory):
        self.residences_file_path = str(residences_file_path)
        self.old_world_directory = str(old_world_directory)
        self.new_world_directory = str(new_world_directory)
        self.residences_amount = 0  # residences found
        self.residences_corner_regions = []  # determine regions of residences
        self.old_region_amount = 0  # original regions amount
        self.regions = []  # list of residences-contained region files
        self.lost_regions = []  # list of regions not found in old directory
        self.available_regions = []  # list of regions found
        self.world_directory_type = -1  # overworld is 0, nether and end are 1
        self.raw_residences_info = []  # residence file in list form

    def check_path_existence(self):
        """
        Check old world directory & residence file existence
        """
        allow = True  # bool init
        directories = [self.old_world_directory]
        for i in directories:
            if not os.path.isdir(i):
                print('Failed\n'
                      'Directory %s not found.' % i)
                allow = False
        files = [os.path.join(self.old_world_directory, 'level.dat'),
                 self.residences_file_path]
        for i in files:
            if not os.path.isfile(i):
                print('Failed\n'
                      'File %s not found.' % i)
                allow = False
        if allow:
            return True
        else:
            sys.exit(1)

    def check_directory_type(self):
        """
        Check directory folder type to locate region files
        Paths assigned in REGION_LOCATION
        Overworld = 0
        Nether = 1
        The End = 2
        """
        for i in range(len(REGION_LOCATION)):
            if os.path.isdir(os.path.join(self.old_world_directory,
                                          REGION_LOCATION[i])):
                self.world_directory_type = i
                return True
        if self.world_directory_type == -1:  # if none of the situations above
            print('Failed\n'
                  'Could not find regions in %s' % self.old_world_directory)
            sys.exit(1)

    def load_residences_file(self):
        """
        Load residences save file
        Read lines to list self.raw_residences_info
        """
        residences_file = open(self.residences_file_path, 'r',
                               encoding='gbk',
                               errors='ignore'
                               )  # open residence file
        self.raw_residences_info = residences_file.readlines()  # file2list
        residences_file.close()  # close residence file
        return True

    def residence_region_corners_fetch(self):
        """
        Fetch residences' rectangles' corners' points' arguments' xz values
        in the Residence-saves format file.
        2 xz points (upper right corner & lower left corner) for 1 residence.
        2 arguments' values (x, z) for 1 point.
        list self.residences_corner_regions in this format (r.x.z.mca):
        [[res0_x1, res1_x1, ...], [res0_z1, res1_z1, ...],
         [res0_x2, res1_x2, ...], [res0_z2, res1_z2, ...]]
        """
        for i in ['X1', 'Z1', 'X2', 'Z2']:  # collect residences data
            coordinate_values = list(map(lambda x: re.findall(': (.*)', x)[0],
                                         [j for j in self.raw_residences_info
                                          if i in j]
                                         )
                                     )  # grab number values from lines
            region_values = list(map(lambda x: math.floor(int(x) / REGION_SIZE
                                                          ),
                                     coordinate_values
                                     )
                                 )  # transform coordinate to region values
            self.residences_corner_regions.append(region_values)
        self.residences_amount = len(self.residences_corner_regions[0])
        print('Residences found: %d' % self.residences_amount)
        return True

    def check_residences_integrity(self):
        """
        Check values of residences' corners' values
        Check if len(X1) == len(X2) == len(Z1) == len(Z2)
        """
        points_amounts = list(map(lambda x: len(x),
                                  self.residences_corner_regions
                                  )
                              )
        if all(i == self.residences_amount for i in points_amounts):
            #  check values are all in correct pairs
            return True
        else:
            print('Failed\n'
                  'Residence file format error.')
            sys.exit(1)

    def covered_regions_calculate(self):
        """
        Calculate regions covered by residences' areas.
        Generate a list self.region of region file names.
        Designed for Residence version 4.9.1.9, X2 > X1, Z2 > Z1.
        """
        for i in range(self.residences_amount):
            for j in range(self.residences_corner_regions[2][i],
                           self.residences_corner_regions[0][i] + 1):
                for k in range(self.residences_corner_regions[3][i],
                               self.residences_corner_regions[1][i] + 1):
                    file = FILE_NAME_FORMAT.replace('x', str(j)).replace(
                        'z', str(k))
                    if file not in self.regions:
                        self.regions.append(file)

        print('Covered regions: %d' % len(self.regions))
        return True

    def mkdir_new_directories(self):
        """
        Make new directory for the new world and region directory
        """
        if os.path.exists(self.new_world_directory):  # if already exists
            print('\n@@@@@@@@----CAUTION----@@@@@@@@\n'
                  'New world directory path is already used.\n'
                  'This program will remove this file / directory:\n'
                  '%s\n'
                  'Overwrite it? Please type \'CONFIRM OVERWRITE\' to '
                  'confirm operation. '
                  % self.new_world_directory)
            if input('>>> ') == 'CONFIRM OVERWRITE':  # if confirm delete
                print('Operation Confirmed.')
                if os.path.isdir(self.new_world_directory):  # if directory
                    shutil.rmtree(self.new_world_directory)
                    print('Directory %s deleted.\n' %
                          self.new_world_directory)
                elif os.path.isfile(self.new_world_directory):  # if file
                    os.remove(self.new_world_directory)
                    print('File %s deleted.\n' % self.new_world_directory)
            else:  # if refuse delete
                print('Operation Cancelled.')
                sys.exit(1)

        try:  # if not already exists or already deleted
            os.makedirs(self.new_world_directory)  # mkdir new world directory
            os.makedirs(os.path.join(self.new_world_directory,
                                     REGION_LOCATION[
                                         self.world_directory_type
                                     ]
                                     )
                        )  # mkdir new region directory
        except PermissionError:  # if no permission
            print('Failed\n'
                  'Permission Denied when mkdir.')
            sys.exit(1)
        else:
            return True

    def check_regions_integrity(self):
        """
        Check if all residences regions are in the original region directory.
        """
        old_region_directory = os.path.join(self.old_world_directory,
                                            REGION_LOCATION[
                                                self.world_directory_type
                                            ])
        old_regions = os.listdir(old_region_directory)
        self.lost_regions = list(set(self.regions).difference(set(
            old_regions)))
        for i in self.lost_regions:
            print('%s not found in %s. Continuing...' % (i,
                                                         old_region_directory)
                  )
        self.available_regions = [i for i in self.regions if i not in
                                  self.lost_regions]
        return True

    def copy_level_dat(self):
        """
        Copy level.dat to new directory.
        """
        # touch file
        open(os.path.join(self.new_world_directory, 'level.dat'), "x")
        # copy data
        shutil.copyfile(os.path.join(self.old_world_directory, 'level.dat'),
                        os.path.join(self.new_world_directory, 'level.dat'))
        return True

    def copy_regions(self):
        """
        Copy residence region files to region in new directory.
        """
        old_region_directory = os.path.join(self.old_world_directory,
                                            REGION_LOCATION[
                                                self.world_directory_type
                                            ])
        new_region_directory = os.path.join(self.new_world_directory,
                                            REGION_LOCATION[
                                                self.world_directory_type
                                            ])
        for i in self.available_regions:
            open(os.path.join(new_region_directory, i), "x")  # touch file
            shutil.copyfile(os.path.join(old_region_directory, i),
                            os.path.join(new_region_directory, i))  # copy data
        self.old_region_amount = len(os.listdir(old_region_directory))
        return True

    def summary(self):
        """
        Print the results
        """
        print('Success\n'
              'Original regions: %d\n'
              'Successful copied regions: %d, Failed regions: %d' %
              (
                  self.old_region_amount, len(self.available_regions),
                  len(self.lost_regions)
              )
              )
        return True

    def run(self):
        """
        Run all the functions in sequence
        """
        self.check_path_existence()
        self.check_directory_type()
        self.load_residences_file()
        self.residence_region_corners_fetch()
        self.check_residences_integrity()
        self.covered_regions_calculate()
        self.mkdir_new_directories()
        self.check_regions_integrity()
        self.copy_level_dat()
        self.copy_regions()
        self.summary()


def cli(argv):
    if len(argv) > 1:  # if has command arguments
        process = ResidencesOnly(argv[1], argv[2], argv[3])
    else:  # run without command arguments
        residences_file_path = input('Residence save file (.yml) '
                                     'path >>> ')
        old_world_directory = input('Input world directory >>> ')
        new_world_directory = input('Output world directory >>> ')
        process = ResidencesOnly(residences_file_path, old_world_directory,
                                 new_world_directory)
    process.run()
    sys.exit(0)


if __name__ == "__main__":
    cli(sys.argv)
