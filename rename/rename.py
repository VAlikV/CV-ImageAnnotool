import cv2
import glob

images = glob.glob("rename/input/*.jpg")
count = 139

for i in images:
    image = cv2.imread(i)

    cv2.imwrite("rename/output/f_" + str(count) + ".jpg", image)

    count += 1