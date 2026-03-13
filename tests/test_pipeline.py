import unittest

from app.pipeline import GameArtPipeline
from app.rag import StyleKnowledgeBase
from app.config import KNOWLEDGE_FILE
from app.web import create_app


class TestRag(unittest.TestCase):
    def test_retrieve_returns_results(self):
        kb = StyleKnowledgeBase.from_json(KNOWLEDGE_FILE)
        docs = kb.retrieve("赛博朋克 女刺客", top_k=2)
        self.assertTrue(len(docs) > 0)

    def test_chinese_ancient_style_prefers_ink_wash(self):
        kb = StyleKnowledgeBase.from_json(KNOWLEDGE_FILE)
        docs = kb.retrieve("中国古风男性刺客，水墨风", top_k=3)
        self.assertTrue(len(docs) >= 1)
        self.assertEqual(docs[0]["style"], "Ink Wash")
        self.assertLessEqual(len(docs), 2)


class TestPipeline(unittest.TestCase):
    def test_generate_returns_required_fields(self):
        pipe = GameArtPipeline()
        result = pipe.generate("设计一个赛博朋克风格的女性刺客角色")
        self.assertIn("image", result)
        self.assertIn("enhanced_prompt", result)
        self.assertTrue(result["enhanced_prompt"])
        self.assertIn(result.get("backend"), {"stable-diffusion", "mock"})
        self.assertIn("model_id", result)
        self.assertIn("device", result)


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_generate_endpoint_success(self):
        resp = self.client.post("/generate", json={"description": "赛博朋克女刺客"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("image", data)
        self.assertTrue(len(data["image"]) > 100)
        self.assertIn(data.get("backend"), {"stable-diffusion", "mock"})

    def test_generate_endpoint_validation_error(self):
        resp = self.client.post("/generate", json={"description": ""})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
