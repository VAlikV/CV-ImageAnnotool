import cv2
import numpy as np

# Путь к файлам
image_path = 'input/1.png'
label_path = 'output/1.txt'

# Загрузка изображения
image = cv2.imread(image_path)
h, w = image.shape[:2]

# Чтение разметки
with open(label_path, 'r') as f:
    lines = f.readlines()

# Перебираем все аннотированные объекты
for line in lines:
    parts = line.strip().split()
    cls_id = int(parts[0])
    coords = list(map(float, parts[1:]))
    points = np.array([
        [int(float(coords[i]) * w), int(float(coords[i+1]) * h)]
        for i in range(0, len(coords), 2)
    ])

    # Рисуем полигон
    cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.fillPoly(image, [points], color=(0, 255, 0, 50))  # заливаем полигон полупрозрачным

# Показываем результат
cv2.imshow('Segmentation Overlay', image)
cv2.waitKey(0)
cv2.destroyAllWindows()