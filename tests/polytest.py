import numpy as np
import cv2

def create_yolo_line_from_mask(class_id, mask, image_width, image_height):
    # Убедимся, что маска uint8
    binary_mask = (mask > 0).astype(np.uint8) * 255

    # Найдём внешние контуры (только один объект)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None  # Ничего не нашли

    # Выберем самый большой по площади контур
    contour = max(contours, key=cv2.contourArea)
    
    # Вычислим bbox
    x, y, w, h = cv2.boundingRect(contour)
    x_center = (x + w / 2) / image_width
    y_center = (y + h / 2) / image_height
    width = w / image_width
    height = h / image_height

    # Преобразуем контур в YOLO-формат
    norm_points = []
    for pt in contour:
        px, py = pt[0]
        norm_x = px / image_width
        norm_y = py / image_height
        norm_points.append((norm_x, norm_y))

    # Соберём строку
    bbox_part = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
    mask_part = " ".join(f"{x:.6f} {y:.6f}" for (x, y) in norm_points)

    # return f"{bbox_part} {mask_part}"
    return x_center, y_center, width, height, norm_points

# ======================================================================
# ======================================================================
# ======================================================================

mask = np.load('../test.npy', mmap_mode='r')
print(mask)

# x_center, y_center, width, height, norm_points = create_yolo_line_from_mask(0, mask, mask.shape[1], mask.shape[0])

with open("../output/connector0.txt", "r") as f:
    a = f.read()

params = [float(i) for i in a.split()]

x_center = params[1]
y_center = params[2]
width = params[3]
height = params[4]
norm_points = []
points = params[5:]
for i in range(len(points)//2):
    norm_points.append((points[2*i], points[2*i+1]))

current_mask = np.zeros((*mask.shape, 3), dtype=np.uint8)  # shape: (H, W, 3)
current_mask[mask == 1] = [255,0,0]  # BGR

print(width)

current_mask = cv2.rectangle(current_mask, pt1=(round((x_center-width/2)*mask.shape[1]), round((y_center-height/2)*mask.shape[0])), pt2=(round((x_center+width/2)*mask.shape[1]), round((y_center+height/2)*mask.shape[0])), color=(0,255,0))

for p in norm_points:
    current_mask = cv2.circle(current_mask, (round(p[0]*mask.shape[1]), round(p[1]*mask.shape[0])), 0, (0,0,255), -1)
    
cv2.imshow("Mask", current_mask)

cv2.waitKey(0)
cv2.destroyAllWindows()

# with open("file.txt", "w") as f:
#     f.write("Alik" + "\n")
#     f.write("Alik2")