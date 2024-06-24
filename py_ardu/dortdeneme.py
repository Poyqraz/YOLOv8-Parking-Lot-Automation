import torch
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Modeli yükleme
model = YOLO('parklast.pt')  # Eğitilmiş model dosyanızın yolu

# Resmi yükleme
image_path = 'carpark.mp4'
image = cv2.imread(image_path)

# Modeli kullanarak tahmin yapma
results = model(image)

# Tahmin edilen bounding box'ları ve sınıfları alma
detections = results.pred[0].cpu().numpy()  # [x_min, y_min, x_max, y_max, confidence, class]

# Park alanlarını belirlemek için dolu ve boş alanları sayma
occupied_count = 0
available_count = 0

for det in detections:
    x_min, y_min, x_max, y_max, conf, cls = det
    if cls == 1:  # Dolu park alanı sınıfı (örneğin 1)
        occupied_count += 1
    elif cls == 0:  # Boş park alanı sınıfı (örneğin 0)
        available_count += 1

print(f'Dolu park alanı sayısı: {occupied_count}')
print(f'Boş park alanı sayısı: {available_count}')

# Bounding box'ları resmin üzerine çizme
for det in detections:
    x_min, y_min, x_max, y_max, conf, cls = det
    if cls == 1:  # Dolu park alanı
        color = (0, 0, 255)  # Kırmızı
    elif cls == 0:  # Boş park alanı
        color = (0, 255, 0)  # Yeşil
    else:
        continue
    cv2.rectangle(image, (int(x_min), int(y_min)), (int(x_max), int(y_max)), color, 2)

# Sonucu gösterme
plt.figure(figsize=(10, 10))
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.show()

#duyurulara atılan görsel demo