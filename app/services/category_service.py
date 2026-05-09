import json
from typing import List, Dict, Any
from config.settings import settings


class CategoryService:
    def __init__(self):
        self.categories_file = settings.CATEGORIES_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        import os
        if not os.path.exists(self.categories_file):
            default_data = {
                "categories": ["delivery", "billing", "product", "quality", "customer service", "features"],
                "few_shot_examples": []
            }
            with open(self.categories_file, 'w') as f:
                json.dump(default_data, f, indent=2)

    def _load_data(self) -> dict:
        with open(self.categories_file, 'r') as f:
            return json.load(f)

    def _save_data(self, data: dict):
        with open(self.categories_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_all(self) -> dict:
        data = self._load_data()
        return {
            "categories": data.get("categories", []),
            "few_shot_examples": data.get("few_shot_examples", [])
        }

    def get_categories(self) -> List[str]:
        data = self._load_data()
        return data.get("categories", [])

    def get_few_shot_examples(self) -> List[Dict[str, Any]]:
        data = self._load_data()
        return data.get("few_shot_examples", [])

    def add_category(self, category: str) -> bool:
        data = self._load_data()
        categories = data.get("categories", [])

        if category.lower() in [c.lower() for c in categories]:
            return False

        categories.append(category)
        data["categories"] = categories
        self._save_data(data)
        return True

    def update_category(self, old_category: str, new_category: str) -> bool:
        data = self._load_data()
        categories = data.get("categories", [])

        for i, cat in enumerate(categories):
            if cat.lower() == old_category.lower():
                categories[i] = new_category
                data["categories"] = categories
                self._save_data(data)
                return True

        return False

    def delete_category(self, category: str) -> bool:
        data = self._load_data()
        categories = data.get("categories", [])

        for i, cat in enumerate(categories):
            if cat.lower() == category.lower():
                categories.pop(i)
                data["categories"] = categories
                self._save_data(data)
                return True

        return False


category_service = CategoryService()