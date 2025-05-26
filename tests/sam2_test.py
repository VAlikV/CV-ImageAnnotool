import torch
from PIL import Image
from sam2.sam2_image_predictor import SAM2ImagePredictor
import cv2

import numpy as np

# Загрузка изображения
image = Image.open("../input/dcdc0.png").convert("RGB")

# Инициализация предсказателя
predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large")

# Установка изображения
predictor.set_image(image)

# Определение точек ввода
input_points = [[[250, 300]]]  # Замените на ваши координаты
input_labels = [[1]]  # 1 для положительных точек, 0 для отрицательных

# Предсказание масок
with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    masks, _, _ = predictor.predict(point_coords=input_points, point_labels=input_labels)

mask = masks[2]  # [batch, point, num_masks, H, W] → [H, W]

print(masks)

# color = (255,0,0)

# m = mask * 255

# print(m)

# Маску преобразуем в 8-битный формат
mask_uint8 = (mask * 255).astype(np.uint8)

# Преобразуем PIL.Image (RGB) в OpenCV BGR
image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

# Создаем цветную маску (например, красную)
color_mask = np.zeros_like(image_bgr)
color_mask[:, :, 2] = mask_uint8  # Красный канал

overlay = cv2.addWeighted(image_bgr, 1.0, color_mask, 0.5, 0)

cv2.imshow("Mask", overlay)
cv2.waitKey(0)
cv2.destroyAllWindows()