from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
from collections import defaultdict, Counter
import math

app = Flask(__name__)

# Data storage (in-memory for POC)
users = {}
posts = []
comments = []
reactions = []

# Reaction types
REACTION_TYPES = ['like', 'love', 'angry', 'laugh', 'interested', 'empathy']

# Political dimensions for user classification
DIMENSIONS = ['left_right', 'liberal_conservative', 'zionist_anti']

class User:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name
        self.profile = {dim: 0.0 for dim in DIMENSIONS}  # -1 to 1 scale
        self.reaction_history = []
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'profile': self.profile
        }

class Post:
    def __init__(self, post_id, author_id, content):
        self.id = post_id
        self.author_id = author_id
        self.content = content
        self.timestamp = datetime.now()
        self.reactions = []
        self.diversity_score = 0.0
        
    def to_dict(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'author_name': users[self.author_id].name,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'reactions': self.reactions,
            'diversity_score': self.diversity_score
        }

class Comment:
    def __init__(self, comment_id, post_id, author_id, content):
        self.id = comment_id
        self.post_id = post_id
        self.author_id = author_id
        self.content = content
        self.timestamp = datetime.now()
        self.reactions = []
        self.diversity_score = 0.0
        
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'author_name': users[self.author_id].name,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'reactions': self.reactions,
            'diversity_score': self.diversity_score
        }

class Reaction:
    def __init__(self, user_id, target_type, target_id, reaction_type):
        self.user_id = user_id
        self.target_type = target_type  # 'post' or 'comment'
        self.target_id = target_id
        self.reaction_type = reaction_type
        self.timestamp = datetime.now()

def calculate_diversity_score(reactions_list):
    """
    חישוב ציון גיוון על בסיס שונות בפרופילים של המגיבים
    ככל שיש יותר שונות בין המגיבים, הציון גבוה יותר
    """
    if len(reactions_list) < 2:
        return 0.0
    
    # קבלת פרופילים של כל המגיבים
    user_profiles = []
    for reaction in reactions_list:
        user = users.get(reaction.user_id)
        if user:
            user_profiles.append(user.profile)
    
    if len(user_profiles) < 2:
        return 0.0
    
    # חישוב variance ממוצע בכל ממד
    total_variance = 0.0
    for dimension in DIMENSIONS:
        values = [profile[dimension] for profile in user_profiles]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        total_variance += variance
    
    # נרמול (ערך מקסימלי הוא 4 - כשיש variance מקסימלי בכל ממד)
    # נחזיר ערך בין 0 ל-100
    diversity_score = (total_variance / (len(DIMENSIONS) * 4)) * 100
    
    return round(diversity_score, 2)

def update_user_profile_from_reactions():
    """
    עדכון פרופיל משתמש על בסיס התגובות שלו
    אלגוריתם פשוט: משתמש נוטה לכיוון של המשתמשים שהוא מגיב להם חיוביות
    """
    for user_id, user in users.items():
        positive_reactions = ['like', 'love', 'interested', 'empathy']
        
        # מציאת כל התגובות החיוביות של המשתמש
        user_positive_reactions = [
            r for r in reactions 
            if r.user_id == user_id and r.reaction_type in positive_reactions
        ]
        
        if not user_positive_reactions:
            continue
        
        # מציאת למי המשתמש הגיב
        target_profiles = []
        for reaction in user_positive_reactions:
            if reaction.target_type == 'post':
                post = next((p for p in posts if p.id == reaction.target_id), None)
                if post:
                    target_profiles.append(users[post.author_id].profile)
            elif reaction.target_type == 'comment':
                comment = next((c for c in comments if c.id == reaction.target_id), None)
                if comment:
                    target_profiles.append(users[comment.author_id].profile)
        
        if target_profiles:
            # עדכון פרופיל - ממוצע משוקלל
            for dimension in DIMENSIONS:
                avg = sum(p[dimension] for p in target_profiles) / len(target_profiles)
                # הזז את הפרופיל של המשתמש לכיוון הממוצע (0.1 factor)
                user.profile[dimension] = user.profile[dimension] * 0.9 + avg * 0.1

# API Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users', methods=['GET', 'POST'])
def handle_users():
    if request.method == 'POST':
        data = request.json
        user_id = len(users) + 1
        user = User(user_id, data['name'])
        
        # אתחול אקראי של פרופיל (לצורך POC)
        import random
        for dimension in DIMENSIONS:
            user.profile[dimension] = random.uniform(-1, 1)
        
        users[user_id] = user
        return jsonify(user.to_dict()), 201
    
    return jsonify([user.to_dict() for user in users.values()])

@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'POST':
        data = request.json
        post_id = len(posts) + 1
        post = Post(post_id, data['author_id'], data['content'])
        posts.append(post)
        return jsonify(post.to_dict()), 201
    
    # מיון לפי diversity score
    sorted_posts = sorted(posts, key=lambda p: p.diversity_score, reverse=True)
    return jsonify([post.to_dict() for post in sorted_posts])

@app.route('/api/comments', methods=['POST'])
def create_comment():
    data = request.json
    comment_id = len(comments) + 1
    comment = Comment(comment_id, data['post_id'], data['author_id'], data['content'])
    comments.append(comment)
    return jsonify(comment.to_dict()), 201

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    post_comments = [c for c in comments if c.post_id == post_id]
    sorted_comments = sorted(post_comments, key=lambda c: c.diversity_score, reverse=True)
    return jsonify([comment.to_dict() for comment in sorted_comments])

@app.route('/api/reactions', methods=['POST'])
def create_reaction():
    data = request.json
    reaction = Reaction(
        data['user_id'],
        data['target_type'],
        data['target_id'],
        data['reaction_type']
    )
    reactions.append(reaction)
    
    # עדכון התגובות על האובייקט המתאים
    if data['target_type'] == 'post':
        post = next((p for p in posts if p.id == data['target_id']), None)
        if post:
            post.reactions.append({
                'user_id': reaction.user_id,
                'type': reaction.reaction_type
            })
            # חישוב מחדש של diversity score
            post_reactions = [r for r in reactions if r.target_type == 'post' and r.target_id == post.id]
            post.diversity_score = calculate_diversity_score(post_reactions)
    
    elif data['target_type'] == 'comment':
        comment = next((c for c in comments if c.id == data['target_id']), None)
        if comment:
            comment.reactions.append({
                'user_id': reaction.user_id,
                'type': reaction.reaction_type
            })
            # חישוב מחדש של diversity score
            comment_reactions = [r for r in reactions if r.target_type == 'comment' and r.target_id == comment.id]
            comment.diversity_score = calculate_diversity_score(comment_reactions)
    
    # עדכון פרופילי משתמשים
    update_user_profile_from_reactions()
    
    return jsonify({'status': 'success'}), 201

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """סטטיסטיקות כלליות"""
    return jsonify({
        'total_users': len(users),
        'total_posts': len(posts),
        'total_comments': len(comments),
        'total_reactions': len(reactions),
        'avg_diversity_score': sum(p.diversity_score for p in posts) / len(posts) if posts else 0
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
