from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
from collections import defaultdict, Counter
import math
import random

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

# Demo data
DEMO_USERS = [
    # Right-wing users
    {"name": "Sarah Cohen", "profile": {"left_right": 0.8, "liberal_conservative": 0.7, "zionist_anti": 0.9}},
    {"name": "David Levy", "profile": {"left_right": 0.9, "liberal_conservative": 0.8, "zionist_anti": 0.95}},
    {"name": "Rachel Ben-David", "profile": {"left_right": 0.7, "liberal_conservative": 0.6, "zionist_anti": 0.85}},
    {"name": "Moshe Katz", "profile": {"left_right": 0.85, "liberal_conservative": 0.75, "zionist_anti": 0.9}},
    
    # Left-wing users
    {"name": "Yael Shapira", "profile": {"left_right": -0.8, "liberal_conservative": -0.7, "zionist_anti": -0.6}},
    {"name": "Ron Avraham", "profile": {"left_right": -0.85, "liberal_conservative": -0.75, "zionist_anti": -0.7}},
    {"name": "Noa Friedman", "profile": {"left_right": -0.75, "liberal_conservative": -0.8, "zionist_anti": -0.5}},
    {"name": "Amir Goldstein", "profile": {"left_right": -0.7, "liberal_conservative": -0.65, "zionist_anti": -0.55}},
    
    # Centrist/moderate users
    {"name": "Maya Rosenberg", "profile": {"left_right": 0.1, "liberal_conservative": 0.2, "zionist_anti": 0.3}},
    {"name": "Tom Israeli", "profile": {"left_right": -0.1, "liberal_conservative": 0.15, "zionist_anti": 0.25}},
    {"name": "Dana Miller", "profile": {"left_right": 0.05, "liberal_conservative": -0.1, "zionist_anti": 0.2}},
    {"name": "Eyal Bar", "profile": {"left_right": -0.05, "liberal_conservative": 0.05, "zionist_anti": 0.15}},
    
    # Liberal-right users
    {"name": "Lior Stern", "profile": {"left_right": 0.6, "liberal_conservative": -0.5, "zionist_anti": 0.7}},
    {"name": "Tamar Green", "profile": {"left_right": 0.5, "liberal_conservative": -0.6, "zionist_anti": 0.65}},
    
    # Conservative-left users
    {"name": "Avi Klein", "profile": {"left_right": -0.6, "liberal_conservative": 0.5, "zionist_anti": 0.4}},
    {"name": "Shira Mizrahi", "profile": {"left_right": -0.55, "liberal_conservative": 0.55, "zionist_anti": 0.45}},
]

DEMO_POSTS = [
    # Right-wing posts
    {"content": "We need strong security measures to protect our borders and citizens. Safety first!", "author_bias": "right"},
    {"content": "Traditional family values are the foundation of our society. We must preserve them.", "author_bias": "right"},
    {"content": "Free market economy drives innovation and prosperity. Less government intervention!", "author_bias": "right"},
    
    # Left-wing posts
    {"content": "Universal healthcare is a human right. Everyone deserves access to quality medical care.", "author_bias": "left"},
    {"content": "We need to address climate change urgently. Green energy is the future!", "author_bias": "left"},
    {"content": "Social equality and workers' rights should be our top priority.", "author_bias": "left"},
    
    # Centrist/bridging posts
    {"content": "Let's find common ground on education reform. Our children deserve the best.", "author_bias": "center"},
    {"content": "Economic growth AND environmental protection - we can achieve both!", "author_bias": "center"},
    {"content": "Technology is transforming our lives. How can we use it responsibly?", "author_bias": "center"},
    
    # Controversial but could attract diverse views
    {"content": "What's your view on balancing personal freedom with public health measures?", "author_bias": "center"},
    {"content": "Can we discuss immigration policy without the political rhetoric?", "author_bias": "center"},
    {"content": "The role of government in the 21st century - what should it be?", "author_bias": "center"},
]

def calculate_political_alignment(profile1, profile2):
    """Calculate alignment between two political profiles (0-1, higher = more aligned)"""
    total_distance = 0
    for dimension in DIMENSIONS:
        total_distance += (profile1[dimension] - profile2[dimension]) ** 2
    
    # Convert distance to alignment (closer = higher alignment)
    max_distance = len(DIMENSIONS) * 4  # Maximum possible distance
    alignment = 1 - (total_distance / max_distance)
    return max(0, alignment)

def get_post_political_lean(post_content):
    """Determine political lean of post based on content"""
    for demo_post in DEMO_POSTS:
        if demo_post['content'] == post_content:
            return demo_post['author_bias']
    return 'center'

def should_user_react_to_post(user, post, post_bias):
    """Determine if user should react to post and what reaction"""
    user_profile = user.profile
    
    # Calculate political distance
    if post_bias == 'right':
        post_profile = {'left_right': 0.8, 'liberal_conservative': 0.7, 'zionist_anti': 0.8}
    elif post_bias == 'left':
        post_profile = {'left_right': -0.8, 'liberal_conservative': -0.7, 'zionist_anti': -0.5}
    else:  # center
        post_profile = {'left_right': 0.0, 'liberal_conservative': 0.0, 'zionist_anti': 0.2}
    
    alignment = calculate_political_alignment(user_profile, post_profile)
    
    # Probability of reacting increases with alignment
    react_probability = 0.3 + (alignment * 0.6)  # 30-90% chance
    
    if random.random() > react_probability:
        return None
    
    # Choose reaction based on alignment
    if alignment > 0.7:  # Strong agreement
        return random.choice(['like', 'love', 'interested'])
    elif alignment > 0.5:  # Moderate agreement
        return random.choice(['like', 'interested', 'empathy'])
    elif alignment > 0.3:  # Neutral/curious
        return random.choice(['interested', 'empathy', 'laugh'])
    else:  # Disagreement
        if random.random() < 0.3:  # 30% chance to engage with opposing views
            return random.choice(['interested', 'empathy'])
        else:
            return random.choice(['angry', 'laugh'])  # More likely to express disagreement
    
def initialize_demo_data():
    """Initialize demo users, posts, and reactions"""
    global users, posts, comments, reactions
    
    # Clear existing data
    users.clear()
    posts.clear()
    comments.clear()
    reactions.clear()
    
    # Create demo users
    for i, demo_user in enumerate(DEMO_USERS, 1):
        user = User(i, demo_user['name'])
        user.profile = demo_user['profile'].copy()
        users[i] = user
    
    # Create demo posts
    user_ids = list(users.keys())
    for i, demo_post in enumerate(DEMO_POSTS, 1):
        # Select appropriate author based on post bias
        post_bias = demo_post['author_bias']
        if post_bias == 'right':
            author_id = random.choice([1, 2, 3, 4])  # Right-wing users
        elif post_bias == 'left':
            author_id = random.choice([5, 6, 7, 8])  # Left-wing users
        else:
            author_id = random.choice([9, 10, 11, 12])  # Centrist users
        
        post = Post(i, author_id, demo_post['content'])
        posts.append(post)
        
        # Generate reactions from users
        for user_id, user in users.items():
            if user_id == author_id:
                continue  # User doesn't react to their own post
            
            reaction_type = should_user_react_to_post(user, post, post_bias)
            if reaction_type:
                reaction = Reaction(user_id, 'post', post.id, reaction_type)
                reactions.append(reaction)
                post.reactions.append({
                    'user_id': user_id,
                    'type': reaction_type
                })
        
        # Calculate diversity score
        post_reactions = [r for r in reactions if r.target_type == 'post' and r.target_id == post.id]
        post.diversity_score = calculate_diversity_score(post_reactions)
    
    print(f"Demo initialized: {len(users)} users, {len(posts)} posts, {len(reactions)} reactions")

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

@app.route('/api/demo/initialize', methods=['POST'])
def initialize_demo():
    """Initialize demo mode with sample data"""
    initialize_demo_data()
    return jsonify({'status': 'success', 'message': 'Demo data initialized'})

@app.route('/api/demo/reset', methods=['POST'])
def reset_demo():
    """Reset all data"""
    users.clear()
    posts.clear()
    comments.clear()
    reactions.clear()
    return jsonify({'status': 'success', 'message': 'All data cleared'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
