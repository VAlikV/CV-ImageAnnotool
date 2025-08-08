import cv2
import glob

images = glob.glob("rename/input/*.png")
count = 1

for i in images:
    image = cv2.imread(i)

    cv2.imwrite("rename/output/" + str(count) + "_1.png", image)

    count += 1