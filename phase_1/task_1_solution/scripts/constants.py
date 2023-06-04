import cv2
import numpy as np

FRONT_MASK_01 = cv2.imread('../images/front_vision_mask_01.png', 0)
FRONT_MASK_02 = cv2.imread('../images/front_vision_mask_02.png', 0)
FRONT_MASK_03 = cv2.imread('../images/front_vision_mask_03.png', 0)

DEFAULT_SEG_CRT = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

DARK_AREA_CROP_YY_THRESH = 325

# NOTE: remember to use the cropped version of
# lateral points when cropping the lateral images
LATERAL_CROP_XX_THRESH = 60

LATERAL_LEFT_VISION_POINT = np.array((420, 300))
LATERAL_RIGHT_VISION_POINT = np.array((420, 180))

CROPPED_LATERAL_LEFT_VISION_POINT = LATERAL_LEFT_VISION_POINT - (LATERAL_CROP_XX_THRESH, 0)
CROPPED_LATERAL_RIGHT_VISION_POINT = LATERAL_RIGHT_VISION_POINT - (LATERAL_CROP_XX_THRESH, 0)

FRONT_VISION_LEFT_POINT = np.array((200, 324)) + (-25, 0)
FRONT_VISION_RIGHT_POINT = np.array((440, 324)) + (25, 0)
