from typing import Any, Optional
from src.sdk import Scanner

class SecureDataset:
    """Wraps a PyTorch dataset to redact secrets during data loading."""
    def __init__(self, dataset: Any, scanner: Optional[Scanner] = None, text_column: str = "text"):
        self.dataset = dataset
        self.text_column = text_column
        self.scanner = scanner or Scanner(obfuscate=True, obfuscate_mode="synthetic")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]
        if isinstance(item, dict) and self.text_column in item:
            item[self.text_column] = self.scanner.redact(item[self.text_column])
        elif isinstance(item, str):
            item = self.scanner.redact(item)
        elif isinstance(item, tuple) or isinstance(item, list):
            # Try to redact the first string element found
            new_item = list(item)
            for i, val in enumerate(new_item):
                if isinstance(val, str):
                    new_item[i] = self.scanner.redact(val)
                    break
            item = tuple(new_item) if isinstance(item, tuple) else new_item
        return item
