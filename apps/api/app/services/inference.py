from functools import lru_cache
from typing import Tuple
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

from app.core.config import settings


class InferenceService:
    def __init__(self) -> None:
        self.model_name = settings.model_name
        self.model_license = settings.model_license
        self.model_revision = settings.model_revision
        self.processor = AutoImageProcessor.from_pretrained(self.model_name, revision=self.model_revision)
        self.model = AutoModelForImageClassification.from_pretrained(self.model_name, revision=self.model_revision)
        self.model.eval()

    def predict(self, image: Image.Image) -> Tuple[str, float]:
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
        confidence, idx = torch.max(probs, dim=0)
        label = self.model.config.id2label[int(idx)]
        return label, float(confidence)


@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    return InferenceService()


def warmup() -> None:
    service = get_inference_service()
    dummy = Image.new("RGB", (224, 224), color="white")
    service.predict(dummy)
