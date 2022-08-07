import argparse
import shutil
import glob
import os
from multiprocessing import Pool


class SorterTool:
    
    def __init__(self, path_dir_input, path_dir_output):
        self.path_input = path_dir_input
        self.path_output = path_dir_output

    def __call__(self):
        """Sort images into directories based on well positions."""
        try:
            paths_files = self.glob_fn()
            wells_positions = self.well_dir_fn(paths_files)
            self.dir_position_make(wells_positions)
            navigations_files = self.navigations_files_prepare(wells_positions)

            pool = Pool()
            _ = pool.starmap(self.file_move_fn, navigations_files)
            pool.close()
            pool.join()
        except RuntimeError as re:
            print('[ERROR][EXCEPTION 1] SorterTool/__call__ \n', re)
        except TypeError as te:
            print('[ERROR][EXCEPTION 2] SorterTool/__call__ \n', te)
        except Exception as e:
            print('[ERROR][EXCEPTION 3] SorterTool/__call__ \n', e)

    def dir_position_make(self, positions):
        """Create directories for positions."""
        for position in positions:
            try:
                dir_path_position = self.path_output + '/' + position
                dir_path_position_image = dir_path_position + '/images'
                os.mkdir(dir_path_position)
                os.mkdir(dir_path_position_image)
            except OSError as ose:
                print('[ERROR] SorterTool/dir_position_make \n', ose)
            except Exception as e:
                print(e)

    @staticmethod
    def file_move_fn(path_file_root, path_file_save):
        """Move a file from its old location to a directory for specified well position."""
        try:
            shutil.move(path_file_root, path_file_save)
        except RuntimeError as re:
            print('[ERROR][EXCEPTION 1] SorterTool/file_move \n', re,
                  f'\n Path file root: {path_file_root} \n Path file save: {path_file_save}')
        except Exception as e:
            print('[ERROR][EXCEPTION 2] SorterTool/file_move \n', e,
                  f'\n Path file root: {path_file_root} \n Path file save: {path_file_save}')

    def glob_fn(self):
        """Get paths of image files in input directory."""
        try:
            paths_files = glob.glob(self.path_input + '/*.tif')
            paths_files.extend(glob.glob(self.path_input + '/*.png'))
            paths_files.extend(glob.glob(self.path_input + '/*.jpg'))
            return paths_files
        except OSError as ose:
            print('[ERROR][EXCEPTION 1] SorterTool/glob_fn \n', ose)
        except Exception as e:
            print('[ERROR][EXCEPTION 2] SorterTool/glob_fn \n', e)

    def navigations_files_prepare(self, well_positions):
        """Prepare filepaths for moving images."""
        try:
            navigations_files = []

            for well_position in well_positions:
                print('[INFO] Creating navigations for {}'.format(well_position), end='\r')
                well_position_paths_files = glob.glob(self.path_input + '/' + well_position + '*.*')

                for well_position_path_file in well_position_paths_files:
                    well_position_name_file = os.path.basename(well_position_path_file)
                    well_position_path_file_save = os.path.join(self.path_output,
                                                                well_position,
                                                                'images',
                                                                well_position_name_file)

                    navigations_files.append((well_position_path_file,
                                              well_position_path_file_save))

            return navigations_files
        except OSError as ose:
            print('[ERROR][EXCEPTION 1] SorterTool/navigations_files_prepare \n', ose)
        except Exception as e:
            print('[ERROR][EXCEPTION 2] SorterTool/navigations_files_prepare \n', e)

    def path_check(self):
        """Convenience function to assert that given paths exist."""
        assert os.path.isdir(self.path_input),\
            f"Path to input directory does not exist: {self.path_input}"
        assert os.path.isdir(self.path_output),\
            f"Path to input directory does not exist: {self.path_output}"

    @staticmethod
    def well_dir_fn(paths_files):
        """Extract well positions of acquisition."""
        try:
            well_positions = []
            for path_file in paths_files:
                name_file = os.path.basename(path_file)
                well_position = name_file[:11]
                well_positions.append(well_position)

            well_positions = sorted(set(well_positions))
            return well_positions
        except OSError as ose:
            print('[ERROR][EXCEPTION 1] SorterTool/well_dir_fn \n', ose)
        except Exception as e:
            print('[ERROR][EXCEPTION 2] SorterTool/well_dir_fn \n', e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path',
                        help='Path to directory containing images.',
                        required=True)
    parser.add_argument('-o', '--output_path',
                        help='Path to save sorted directories to. Standard: Input directory.')
    args = parser.parse_args()

    path_input = args.input_path
    if args.output_path is None:
        path_output = args.input_path
    else:
        path_output = args.output_path

    SorterTool(path_input, path_output)()
