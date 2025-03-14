from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import torch
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = self.load_model()

    def load_model(self):
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
            logger.info(f"Model {self.model_name} loaded successfully")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None

    def generate_response(self, prompt, **kwargs):
        if not self.model:
            logger.error("Model not loaded")
            return None
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, **kwargs)
        
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return response