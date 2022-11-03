"""Provides object detection functionality."""

from typing import Tuple, Any, Union

from paddleocr import PaddleOCR
import cv2 as cv
import numpy as np


class Detection:
    """
    Holds methods related to detecting and working with images.
         
    Methods
    ----------
    find()
        Find 'needle' image on a 'haystack' image.
    get_click_coords()
        Calculate center (x, y) coordinates of bounding box.
    draw_rectangles()
        Draw rectangle(s) on an image.
    draw_markers()
        Draw marker(s) on an image.
    detect_objects()
        Detect 'needle' images on a 'haystack' image.
    detect_objects_with_masks()
        Detect 'needle' images on a 'haystack' image. Uses masks.
    detect_text_from_image()
        Detect text from image.
    generate_image_data()
        Construct a dictionary for use in detect_objects_with_masks().
    
    """

    def find(self, 
             haystack_img: np.ndarray | str,
             needle_img: np.ndarray | str,
             threshold: float = 0.9,
             match_method: int = cv.TM_CCOEFF_NORMED,
             mask: np.ndarray = None) \
             -> tuple | list[list[int]]:
        """
        Find 'needle' image on a 'haystack' image.

        Parameters
        ----------
        haystack_img : np.ndarray or str
            Image to search on.
        needle_img : np.ndarray or str
            Image to search for.
        threshold : float, optional
            Accuracy with which `needle_img` will be searched for 
            (0.0 to 1.0). Defaults to 0.9.
        match_method : int, optional
            Comparison method used by `cv.matchTemplate()`. Defaults to 
            `cv.TM_CCOEFF_NORMED`.

        Returns
        ----------
        rectangles : tuple
            Empty `tuple` if no matches found.
        rectangles : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]]
            of bounding box.

        Raises
        ---------
        Overload resolution failed
            If `haystack_img` or `needle_img` are not `np.ndarray` or 
            `str`.
        (-215:Assertion failed) in function 'cv::matchTemplate'
            If `haystack_img` or `needle_img` do not exist in the 
            specified `str` path.
        (-215:Assertion failed) in function 'cv::matchTemplate'
            If `haystack_img` and `needle_img` are read into memory
            differently.
            Example: `haystack_img` is 'BGR' and `needle_img` is 'GRAY'.

        """
        # If 'haystack_img' or/and 'needle_img' are passed in as 'str'
        # paths to images, convert them to 'numpy.ndarray' by reading 
        # into memory. Otherwise just leave them as they are. Can't
        # store them with the same variable name during conversion 
        # because 'mypy' throws a TypeError.
        if isinstance(haystack_img, str):
            haystack = cv.imread(haystack_img, cv.IMREAD_UNCHANGED)
        else:
            haystack = haystack_img

        if isinstance(needle_img, str):
            needle = cv.imread(needle_img, cv.IMREAD_UNCHANGED)
        else:
            needle = needle_img

        # Using matchTemplate to find 'needle' in 'haystack'.
        result = cv.matchTemplate(haystack, 
                                  needle,
                                  match_method,
                                  mask=mask)

        # Finding best matches (using threshold) and getting the (x, y) 
        # coordinates of top left corners of those matches.
        locations: Any = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        # Creating a list of rectangles that stores bounding box 
        # information of found matches [[topLeft_x, topLeft_y, w, h]].
        # The list is later used in 'cv.groupRectangles()'.
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), 
                    int(loc[1]), 
                    needle.shape[1], 
                    needle.shape[0]]
            # Appending to the list twice because 'cv.groupRectangles()' 
            # requires at least two overlapping rectangles for it group
            # them together. If only appending once, 
            # 'cv.groupRectangles()' will throw out any results 
            # (even if they're correct) that do not overlap.
            rectangles.append(rect)
            rectangles.append(rect)

        # Grouping all rectangles that are close by.
        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.5)
        
        return rectangles

    def get_click_coords(self, 
                         rectangles: list[list[int]],
                         region: Tuple[int, int, int, int] = (0, 0, 0, 0)) \
                         -> list[Tuple[int, int]]:
        """
        Calculate center (x, y) coordinates of bounding box.

        Parameters
        ----------
        rectangles : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]]
            of bounding box.
        region : Tuple[int, int, int, int], optional
            Screen region (topLeft_x, topLeft_y, width, height) where
            image found within `rectangles` was taken. Allows to 
            calculate precise center coordinates of image on the whole 
            screen. Defaults to (0, 0, 0, 0).
        
        Returns
        ----------
        coords : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.

        """
        coords = []
        for [x, y, w, h] in rectangles:
            # Determining the center positions of found matches.
            center_x = x + int(w/2) + region[0]
            center_y = y + int(h/2) + region[1]
            # Saving the center positions.
            coords.append((center_x, center_y))

        return coords

    def draw_rectangles(self, 
                        haystack_img: np.ndarray | str, 
                        rectangles: list[list[int]],
                        line_color: Tuple[int, int, int] = (0, 255, 0),
                        line_thickness: int = 2) \
                        -> Union[np.ndarray[Any, Any], str]:
        """
        Draw rectangle(s) on an image.

        Parameters
        ----------
        haystack_img : np.ndarray or str
            Image to draw on.
        rectangles : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]]
            of bounding box.
        line_color : Tuple[int, int, int], optional
            Color to use for drawing. In 'BGR' format. Defaults to:
            (0, 255, 0).
        line_thickness : int, optional
            Thickness of drawn line(s). Negative value results in a 
            filled rectangle. Defaults to 2.

        Returns
        ----------
        haystack_img : Union[np.ndarray[Any, Any], str]
            Image as `np.ndarray`.

        Raises
        ----------
        Can't open/read file: check file path/integrity
            If path to `haystack_img` is incorrect.

        """
        # Reading 'haystack_img' into memory if it was passed in as
        # a string.
        if isinstance(haystack_img, str):
            haystack_img = cv.imread(haystack_img, cv.IMREAD_UNCHANGED)

        line_color = line_color
        line_thickness = line_thickness

        for [x, y, w, h] in rectangles:
            # Determine the box positions.
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            # Draw the box/rectangle.
            cv.rectangle(haystack_img, 
                         top_left, 
                         bottom_right, 
                         line_color, 
                         line_thickness)

        return haystack_img

    def draw_markers(self, 
                     haystack_img: np.ndarray | str, 
                     coords: list[Tuple[int, int]],
                     marker_color: Tuple[int, int, int] = (0, 255, 0),
                     marker_type: int = cv.MARKER_CROSS) \
                     -> Union[np.ndarray[Any, Any], str]:
        """
        Draw marker(s) on an image.

        Parameters
        ----------
        haystack_img : np.ndarray | str
            Image to draw on.
        coords : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.
        marker_color : Tuple[int, int, int], optional
            Color to use for drawing. In 'BGR' format. Defaults to:
            (0, 255, 0).
        marker_type : int, optional
            Type of marker(s) to draw. Defaults to `cv.MARKER_CROSS`.

        Returns
        ----------
        haystack_img : Union[np.ndarray[Any, Any], str]
            Image as `np.ndarray`.

        Raises
        ----------
        Can't open/read file: check file path/integrity
            If path to `haystack_img` is incorrect.
        
        """
        # Reading 'haystack_img' into memory if it was passed in as
        # a string.
        if isinstance(haystack_img, str):
            haystack_img = cv.imread(haystack_img, cv.IMREAD_UNCHANGED)

        marker_color = marker_color
        marker_type = marker_type

        for (center_x, center_y) in coords:
            # Drawing markers on the center positions of found matches.
            cv.drawMarker(haystack_img, 
                         (center_x, center_y), 
                          marker_color, 
                          marker_type)

        return haystack_img

    def detect_objects(self, 
                       objects_to_detect_list: list[str],
                       objects_to_detect_path: str, 
                       haystack_image: np.ndarray | str, 
                       threshold: float = 0.6,
                       match_method: int = cv.TM_CCOEFF_NORMED) \
                       -> Tuple[list[list[int]], list[Tuple[int, int]]]:
        """
        Detect multiple different 'needle' images on a 'haystack' image.

        Best used when there are two or more different images to be 
        detected. Otherwise use the `find()` method.

        Parameters
        ----------
        objects_to_detect_list : list[str]
            `list` containing `str` names of images to detect.
        objects_to_detect_path : str
            `str` path to location of images.
        haystack_image : np.ndarray or str
            Image to search on.
        threshold : float, optional
            Accuracy with which images will be searched for 
            (0.0 to 1.0). Defaults to 0.6.
        match_method : int, optional
            Comparison method used by `cv.matchTemplate()`. Defaults to 
            `cv.TM_CCOEFF_NORMED`.

        Returns
        ----------
        object_rectangles_converted : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]]
            of bounding box.
        object_center_xy_coordinates : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.
        object_rectangles_converted : tuple
            Empty `tuple` if no matches found.
        object_center_xy_coordinates : list
            Empty `list` if no matches found.

        Raises
        ----------
        (-215:Assertion failed) in function 'cv::matchTemplate'
            If any `str` within `objects_to_detect_list` is incorrect.
        (-215:Assertion failed) in function 'cv::matchTemplate'
            If `objects_to_detect_path` is incorrect.

        """
        # Making sure the path string ends with a '\'.
        if not objects_to_detect_path.endswith("\\"):
            objects_to_detect_path += "\\"

        # Looping over all needle images and trying to find them on the 
        # haystack image. Appending bounding box information of found 
        # matches to an empty list. This generates a list of 2D 
        # numpy arrays.
        object_rectangles = []
        for image in objects_to_detect_list:
            rectangles = self.find(haystack_image, 
                                   objects_to_detect_path + image, 
                                   threshold=threshold,
                                   match_method=match_method)
            object_rectangles.append(rectangles)

        # Converting a list of 2D numpy arrays into a list of 1D numpy 
        # arrays.
        object_rectangles_converted: Any = []
        for i in object_rectangles:
            for j in i:
                object_rectangles_converted.append(j)

        # Converting a list of 1D numpy arrays into one 2D numpy array.
        object_rectangles_converted = np.array(object_rectangles_converted)

        # Grouping all rectangles that are close-by.
        object_rectangles_converted, weights = cv.groupRectangles(
                                                object_rectangles_converted, 
                                                1, 
                                                0.5)

        # Creating a list containing center (x, y) coordinates of found
        # matches.
        object_center_xy_coordinates = self.get_click_coords(
                                                   object_rectangles_converted)

        return object_rectangles_converted, object_center_xy_coordinates

    def detect_objects_with_masks(self,
                                  image_data,
                                  image_list,
                                  haystack_image,
                                  threshold=0.9832,
                                  match_method=cv.TM_CCORR_NORMED):
        """
        Detect multiple different 'needle' images on a 'haystack' image.

        This method uses masks, unlike `detect_objects()`.

        Parameters
        ----------
        image_data : dict[str: Tuple[np.ndarray, np.ndarray]]
            Dictionary containing image information. Can be generated by
            `generate_image_data()` method.
        image_list : list[str]
            `list` of images to search for. These images are used as
            keys to access data in `image_data`.
        haystack_image : np.ndarray
            Image to search on.
        threshold : float, optional
            Detection threshold. Ranges from 0 to 1. Defaults to 0.9832.
        match_method : int, optional
            Comparison method used by `cv.matchTemplate()`. Defaults to 
            `cv.TM_CCORR_NORMED`.

        Returns
        ----------
        rects_list : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]]
            of bounding box.
        coords_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.
        rects_list : tuple
            Empty `tuple` if no matches found.
        coords_list : list
            Empty `list` if no matches found.     
        
        """
        rects = []
        for image in image_list:

            rect = self.find(haystack_image,
                             image_data[image][0],
                             threshold=threshold,
                             match_method=match_method,
                             mask=image_data[image][1])

            if len(rect) > 0:
                rects.append(rect)
                rects.append(rect)

        # Converting a list of 2D numpy arrays into a list of 1D numpy 
        # arrays.
        rects_list = []
        for i in rects:
            for j in i:
                rects_list.append(j)

        # Converting a list of 1D numpy arrays into one 2D numpy array.
        rects_list = np.array(rects_list)

        # Grouping all rectangles that are close-by.
        rects_list, weights = cv.groupRectangles(rects_list, 1, 0.5)

        # Creating a list containing center (x, y) coordinates of found
        # matches.
        coords_list = self.get_click_coords(rects_list)

        return rects_list, coords_list

    def detect_text_from_image(self,
                               image_path: np.ndarray | str,
                               lang: str = "en",
                               use_angle_cls: bool = False,
                               show_log: bool = False) \
                               -> Tuple[list[Tuple[list[int], str]], \
                                        list[list[int]], \
                                        list[str]]:
        """
        Detect text from image.

        Uses CPU only.

        Parameters
        ----------
        image_path : np.ndarray or str
            Image to extract text from.
        lang : str, optional
            Language of text in image. Defaults to English.
        use_angle_cls: bool, optional
            Angle classifier. If `True`, the text with rotation of 180 
            degrees can be recognized. If no text is rotated by 180 
            degrees, use `False` for better performance. Text with 
            rotation of 90 or 270 degrees can be recognized even if 
            `False`. Defaults to `False`.
        show_log : bool, optional
            Whether to print log to terminal. Defaults to `False`.

        Returns
        ----------
        r_and_t : list[Tuple[list[int], str]]
            `list` containing `tuple` of bounding box dimensions as
            `list` and text detected within as `str`. Example:
            [([topLeft_x, topLeft_y, width, height], "string")].
        rectangles : list[list[int]]
            2D `list` containing all bounding boxes of detected
            text. Example: [[topLeft_x, topLeft_y, width, height]].
        text : list[str]
            `list` of all detected text as `str`.

        Raises
        ----------
        Assertion Error
            If `image_path` is incorrect.

        """
        if isinstance(image_path, str):
            image_path = cv.imread(image_path, cv.IMREAD_UNCHANGED)

        ocr = PaddleOCR(lang=lang,
                        use_angle_cls=use_angle_cls,
                        show_log=show_log)

        results = ocr.ocr(image_path, cls=use_angle_cls)
    
        # results[0][0][0] are [x, y] coordinates of the TOP LEFT 
        # corner of the bounding box.
        # results[0][0][2] are [x, y] coordinates of the BOTOOM RIGHT 
        # corner of the bounding box.
        # results[0][1][0] is the text found within the bounding box.
        # results[0][1][1] is the confidence parameter.

        # Getting bounding box information of detected results.
        boxes = [result[0] for result in results]

        # Getting [x, y, w, h] of the bounding boxes. This format is
        # needed for 'draw_rectangles()' method.
        rectangles = [[int(box[0][0]), 
                       int(box[0][1]), 
                       int(box[2][0]) - int(box[0][0]), 
                       int(box[2][1]) - int(box[0][1])] 
                       for box in boxes]
                       
        # Getting all detected text.
        text = [result[1][0] for result in results]

        # Creating a list which stores [x, y, w, h] of the bounding box 
        # and text found within that bounding box.
        r_and_t = []
        for i in range(len(rectangles)):
            r_and_t.append((rectangles[i], text[i]))

        return r_and_t, rectangles, text

    @staticmethod
    def generate_image_data(image_list, image_path):
        """
        Construct a dictionary.

        This method allows for easy creation of a dictionary that is
        used in `detect_objects_with_masks()` method as `image_data` 
        argument.

        Make sure that images in `image_list` are 32 bit depth and
        have transparency (transparent background for example).

        Parameters
        ----------
        image_list : list[str]
            `list` of `str` containing names of image files.
        image_path : str
            Path to folder where images are stored.

        Returns
        ----------
        data : dict[str: Tuple[np.ndarray, np.ndarray]]
            Dictionary containing image information. Name of image
            as key and a `tuple`, that holds respective image's data
            without alpha channel at position 0 and image's mask
            data at position 1, as value.

        Note
        ----------
        Implementation inspired by this answer. Specifically channel
        extraction:
        https://stackoverflow.com/questions/63091761/how-to-improve
        -accuracy-of-opencv-matching-results-in-python

        """
        # Making sure the path string ends with a '\'.
        if not image_path.endswith("\\"):
            image_path += "\\"

        data = {}

        for image in image_list:

            needle = image_path + image
            needle = cv.imread(needle, cv.IMREAD_UNCHANGED)

            # Extracting alpha channel (transparency) from original image.
            needle_mask = needle[:,:,3]

            # Merging extracted alpha channel three times to create a
            # 24 bit image (mask). Image is black & white.
            needle_mask = cv.merge([needle_mask, needle_mask, needle_mask])

            # Extracting all channels (RGB) except alpha (transparency) from
            # original image to create a 24 bit image. Images must be the 
            # same bit depth, otherwise 'cv.matchTemplate()' will throw 
            # an assertion error.
            needle_24bit = needle[:,:,0:3]

            data.update({image: (needle_24bit, needle_mask)})

        return data
