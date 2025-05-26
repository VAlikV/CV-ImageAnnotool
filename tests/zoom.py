import cv2

base_img = cv2.imread("input/dcdc0.png")
base_img = cv2.resize(base_img, (800, 600))

img = base_img.copy()
zoom = 1
min_zoom = 1
max_zoom = 10

x_offset, y_offset = 0, 0

def select_roi(event, x, y, flags, param):
    global base_img, zoom, min_zoom, max_zoom, x_offset, y_offset

    if event == cv2.EVENT_LBUTTONDOWN:
        px = round(x / zoom) + x_offset
        py = round(y / zoom) + y_offset
        print("x: ", px, "y: ", py)

    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            zoom *= 1.1
            zoom = min(zoom, max_zoom)
        else:
            zoom /= 1.1
            zoom = max(zoom, min_zoom)

        img = base_img.copy()

        # Calculate zoomed-in image size
        new_width = round(img.shape[1] / zoom)
        new_height = round(img.shape[0] / zoom)

        # Calculate offset
        x_offset = round(x - (x / zoom))
        y_offset = round(y - (y / zoom))

        # Crop image
        img = img[
            y_offset : y_offset + new_height,
            x_offset : x_offset + new_width,
        ]

        # Stretch image to full size
        img = cv2.resize(img, (base_img.shape[1], base_img.shape[0]))
        cv2.imshow("Selected area", img)


cv2.namedWindow("Selected area")
cv2.setMouseCallback("Selected area", select_roi)
cv2.imshow("Selected area", img)
cv2.waitKey(0)
cv2.destroyAllWindows()