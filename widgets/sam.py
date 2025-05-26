from PIL import Image
import requests
from transformers import AutoModel, AutoProcessor
import matplotlib.pyplot as plt
import torch

class SAM():
    def __init__(self):
        self.model = AutoModel.from_pretrained("facebook/sam-vit-base")
        self.processor = AutoProcessor.from_pretrained("facebook/sam-vit-base")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model.to(self.device)

    def forward(self, image, points, labels):
        inputs = self.processor(images=image, input_points=points, input_labels=labels, return_tensors="pt")
        inputs = {k: v.to(self.device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

        outputs = self.model(**inputs)

        masks = self.processor.post_process_masks(
            outputs.pred_masks, inputs["original_sizes"], inputs["reshaped_input_sizes"]
        )

        # mask = masks[0][0][0].numpy()  # [batch, point, num_masks, H, W] → [H, W]

        return masks