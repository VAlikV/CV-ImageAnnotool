from PIL import Image
import requests
from transformers import AutoModel, AutoProcessor
import matplotlib.pyplot as plt
import torch
import cv2
import numpy as np

model = AutoModel.from_pretrained("facebook/sam-vit-base")
processor = AutoProcessor.from_pretrained("facebook/sam-vit-base")

img_url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/model_doc/sam-car.png"
raw_image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")
input_points = [[[350, 400]]]  # 2D location of a window on the car
inputs = processor(images=raw_image, input_points=input_points, return_tensors="pt")

# Get segmentation mask
outputs = model(**inputs)

# Postprocess masks
masks = processor.post_process_masks(
    outputs.pred_masks, inputs["original_sizes"], inputs["reshaped_input_sizes"]
)

# Получаем первую маску (если несколько — берём только одну)
mask = masks[0][0][0].numpy()  # [batch, point, num_masks, H, W] → [H, W]

# print(mask)

# color = (255,0,0)

# m = mask * 255

# print(m)

# Маску преобразуем в 8-битный формат
mask_uint8 = (mask * 255).astype(np.uint8)

# Преобразуем PIL.Image (RGB) в OpenCV BGR
image_bgr = cv2.cvtColor(np.array(raw_image), cv2.COLOR_RGB2BGR)

# Создаем цветную маску (например, красную)
color_mask = np.zeros_like(image_bgr)
color_mask[:, :, 2] = mask_uint8  # Красный канал

overlay = cv2.addWeighted(image_bgr, 1.0, color_mask, 0.5, 0)

cv2.imshow("Mask", overlay)
cv2.waitKey(0)
cv2.destroyAllWindows()
# Отображаем изображение и накладываем маску
# plt.figure(figsize=(10, 10))
# plt.imshow(raw_image)
# plt.imshow(mask, alpha=0.5, cmap='Reds')  # alpha задаёт прозрачность маски
# plt.axis('off')
# plt.title("Image with Segmentation Mask")
# plt.show()

