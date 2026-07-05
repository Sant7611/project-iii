from django.test import TestCase
from .utils.searchengine import SearchEngine
from .utils.collaborativeRecommender import CollaborativeRecommender


# Create your tests here.
class TfIdfTest(TestCase):

    def setUp(self):
        self.engine = SearchEngine()
        self.engine.add_document(1, "Django Tutorial", "Learn Django framework")
        self.engine.add_document(2, "Flask Guide", "Learn flask framework")
        self.engine.add_document(3, "Python Advanced", "Advanced Python topics")

    def test_rare_word_score_higher(self):
        django_idf = self.engine._idf("django")
        python_idf = self.engine._idf("python")

        self.assertEqual(python_idf, django_idf)

    def test_search_returns_most_relevant_first(self):
        """ARRANGE: engine has docs. ACT: search 'django'."""
        """ASSERT: doc 1 (Django Tutorial) is the only result."""
        results = self.engine.search("django")
        self.assertEqual(len(results), 1)

    def test_search_no_match_returns_empty(self):
        """ARRANGE: engine has no 'react' docs. ACT: search 'react'."""
        """ASSERT: empty list."""
        results = self.engine.search("react")
        self.assertEqual(results, [])

class CosineSimilarityTests(TestCase):
    """Tests for the math behind recommendations."""

    def setUp(self):
        """ARRANGE: Fake Like objects with known user-post pairs."""
        self.rec = CollaborativeRecommender()
        # type() creates fake objects without a database
        likes = [
            type('Like', (), {'user_id': 1, 'post_id': 1}),
            type('Like', (), {'user_id': 1, 'post_id': 2}),
            type('Like', (), {'user_id': 1, 'post_id': 3}),
            type('Like', (), {'user_id': 2, 'post_id': 1}),
            type('Like', (), {'user_id': 2, 'post_id': 2}),
            type('Like', (), {'user_id': 2, 'post_id': 4}),
            type('Like', (), {'user_id': 3, 'post_id': 3}),
            type('Like', (), {'user_id': 3, 'post_id': 4}),
        ]
        self.rec.build_matrix(likes)

    def test_identical_users_have_similarity_one(self):
        """ACT: compare {1,2,3} to itself. ASSERT: perfect similarity."""
        sim = self.rec.cosine_similarity({1, 2, 3}, {1, 2, 3})
        self.assertAlmostEqual(sim, 1.0)

    def test_no_overlap_is_zero(self):
        """ACT: compare {1,2} to {3,4}. ASSERT: nothing in common = 0."""
        sim = self.rec.cosine_similarity({1, 2}, {3, 4})
        self.assertEqual(sim, 0.0)

    def test_partial_overlap_between_zero_and_one(self):
        """ACT: Alice {1,2,3} vs Bob {1,2,4}. ASSERT: score is 2/3."""
        sim = self.rec.cosine_similarity({1, 2, 3}, {1, 2, 4})
        self.assertAlmostEqual(sim, 2 / 3, places=3)

class RecommenderTests(TestCase):
    """Tests for the full recommendation pipeline."""

    def setUp(self):
        """ARRANGE: Same fake data as above."""
        self.rec = CollaborativeRecommender()
        likes = [
            type('Like', (), {'user_id': 1, 'post_id': 1}),
            type('Like', (), {'user_id': 1, 'post_id': 2}),
            type('Like', (), {'user_id': 1, 'post_id': 3}),
            type('Like', (), {'user_id': 2, 'post_id': 1}),
            type('Like', (), {'user_id': 2, 'post_id': 2}),
            type('Like', (), {'user_id': 2, 'post_id': 4}),
            type('Like', (), {'user_id': 3, 'post_id': 3}),
            type('Like', (), {'user_id': 3, 'post_id': 4}),
        ]
        self.rec.build_matrix(likes)

    def test_recommend_returns_new_posts(self):
        """ACT: Get recommendations for Alice (user 1, likes {1,2,3})."""
        """ASSERT: Post 4 (from Bob) is in the results."""
        results = self.rec.recommend(1, n=5)
        post_ids = [post_id for post_id, score in results]
        self.assertIn(4, post_ids)

    def test_user_with_no_likes_gets_empty(self):
        """ACT: Get recommendations for user 99 (never liked anything)."""
        """ASSERT: empty list."""
        results = self.rec.recommend(99, n=5)
        self.assertEqual(results, [])

    def test_recommendations_are_sorted_descending(self):
        """ACT: Get Alice's recommendations. ASSERT: highest score first."""
        results = self.rec.recommend(1, n=5)
        scores = [score for _, score in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
    