from sam2.sam2_image_predictor import SAM2ImagePredictor
from PIL import Image
import requests
import matplotlib.pyplot as plt
import torch

class SAM2():
    def __init__(self):
        self.predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-large")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # self.predictor.to(self.device)

    def forward(self, image, points, labels):

        self.predictor.set_image(image)

        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            masks, _, _ = self.predictor.predict(point_coords=points, point_labels=labels)

        # mask = masks[2]  # [batch, point, num_masks, H, W] → [H, W]

        return masks