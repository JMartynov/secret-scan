import pytest
from src.sdk import Scanner
from src.integrations.pytorch import SecureDataset
from tests.test_sdk_core import MockDetector

class MockDataset:
    def __init__(self, data):
        self.data = data
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        return self.data[idx]

@pytest.fixture
def scanner():
    s = Scanner(obfuscate=True)
    s.engine = MockDetector()
    return s

def test_pytorch_secure_dataset_dict(scanner):
    raw_data = [{"text": "Hello"}, {"text": "My key ghp_12345"}]
    dataset = MockDataset(raw_data)
    secure_dataset = SecureDataset(dataset, scanner=scanner)

    assert secure_dataset[0]["text"] == "Hello"
    assert "ghp_12345" not in secure_dataset[1]["text"]
    assert "g...5" in secure_dataset[1]["text"]

def test_pytorch_secure_dataset_tuple(scanner):
    raw_data = [("Hello", 0), ("My key ghp_12345", 1)]
    dataset = MockDataset(raw_data)
    secure_dataset = SecureDataset(dataset, scanner=scanner)

    assert secure_dataset[0][0] == "Hello"
    assert "ghp_12345" not in secure_dataset[1][0]
    assert "g...5" in secure_dataset[1][0]
