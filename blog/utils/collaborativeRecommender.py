from collections import defaultdict
import math

class CollaborativeRecommender:
    def __init__(self):
        self.user_items = defaultdict(set)
        self.item_users = defaultdict(set)

    
    def build_matrix(self, likes):
        self.user_items.clear()
        self.item_users.clear()

        for like in likes:
            self.user_items[like.user_id].add(like.post_id)
            self.item_users[like.post_id].add(like.user_id)

    def cosine_similarity(self, user1_items, user2_items):
        intersection = len(user1_items & user2_items)
        if not intersection:
            return 0.0
        
        return intersection / math.sqrt(len(user1_items) * len(user2_items))

    def get_similar_users(self, target_user_id, n=5):
        target_items = self.user_items.get(target_user_id, set())
        if not target_items:
            return []
        
        similarities = []
        for user_id, items in self.user_items.items():
            if user_id == target_user_id:
                continue

            sim = self.cosine_similarity(target_items, items)
            if sim >0:
                similarities.append((user_id,sim))

        return sorted(similarities, key=lambda x:x[1], reverse=True)[:n]
    
    def recommend(self, target_user_id, n=5):
        target_items = self.user_items.get(target_user_id, set())
        similar_users = self.get_similar_users(target_user_id, n=10)

        scores = defaultdict(float)

        for user_id, similarity in similar_users:
            for post_id in self.user_items[user_id]:
                if post_id not in target_items:
                    scores[post_id] += similarity

        return sorted(scores.items(), key=lambda x:x[1], reverse=True)[:n]