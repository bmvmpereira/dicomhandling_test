import pydicom 
from scipy.ndimage import gaussian_filter, rotate
import imageio

import glob
import os
import sys

class DcmReader:
    # Class DcmReader - Given a DICOM file path, it constructs an object with two attributes: file's image data and the Image Patient Positition DICOM tag's value
    def __init__(self, path):
        dcm_file = pydicom.dcmread(path)
        self.original = dcm_file.pixel_array
        self.ipp = dcm_file.ImagePositionPatient
    
class DcmFilter(DcmReader):
    # Class DcmFilter - Inherits from DcmReader the attributes 'original' and 'ipp'. 
    # It constructs an object with an extra attribute: a Gaussian Filtered image with a standard sigma of 3.
    def __init__(self, path, sigma = 3):    
        super().__init__(path)
        self.filtered = gaussian_filter(self.original, sigma)
        
class DcmRotate(DcmReader):
    # Class DcmRotater - Inherits from DcmReader the attributes 'original' and 'ipp'. 
    # It constructs an object with an extra attribute: a rotated image with a standard rotation angle of 180.
    def __init__(self, path, angle = 180):
        super().__init__(path)
        self.rotated = rotate(self.original, angle) # Should I limit angle rotation
    
def check_ipp(dcm_filter, dcm_rotate):
    # Given to objects from classes inheriting DcmReader, it compares their ipp and outputs a boolean (True if ipps are equal)
    return dcm_filter.ipp == dcm_rotate.ipp  


class IncorrectNumberOfImages(Exception):
    "Raised when there are more than 2 DICOM files."
    pass

class SameImagePositionPatient(Exception):
    "Raised when the ImagePositionPatient is the same for both DICOM files."
    pass

if __name__ == "__main__":
    path = ' '.join(sys.argv[1:]) #r'C:\\Users\\320089829.CODE1\\Downloads\\RD_code_test\\T1_3D_TFE - 301' #
    dcm_files_list = glob.glob(path + '\\*.dcm') # List of files in 'path' directory with '.dcm' extension
    nb_dcm_files = len(dcm_files_list)
    
    try:
        if nb_dcm_files > 2:
            raise IncorrectNumberOfImages # Raises the mentioned error and does not run the following code
        
        dcm_filter1 = DcmFilter(dcm_files_list[0]) # The DcmFilter object created from the first DICOM files
        dcm_filter2 = DcmFilter(dcm_files_list[1]) # The DcmFilter object created from the second DICOM files

        try:
            if check_ipp(dcm_filter1, dcm_filter2):
                raise SameImagePositionPatient # Raises the mentioned error and does not run the following code
            
            unfiltered_residue = dcm_filter1.original - dcm_filter2.original # Subtraction of the unfiltered images 
            filtered_residue = dcm_filter1.filtered - dcm_filter2.filtered # Subtraction of the filtered images
            
            output_path = path + '\\residues' 
            if not os.path.isdir(output_path): 
                os.mkdir(output_path) # Create output path if it does not yet exist
            
            imageio.imwrite(output_path + r"\\unfiltered_residue.png", unfiltered_residue) # Save with png with imageio in order to maintain 16bit depth. Also read with imageio
            imageio.imwrite(output_path + r"\\filtered_residue.png", filtered_residue)
            
        except SameImagePositionPatient:
            print("The DICOM files appear to be the same. Aborting.")
            print()
            
    except IncorrectNumberOfImages:
        print("Incorrect number of images. Aborting.")
        print()