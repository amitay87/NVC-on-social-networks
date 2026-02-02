# POC - Bridge (Temporary name) - Social Network with Diversity Score 

[English](#english) | [עברית](#hebrew)

---

<a name="english"></a>
## English

### What is this?

A basic system that ranks content by the **diversity** of people reacting to it, rather than just by the number of likes.

### Development Approach

We're pursuing two parallel tracks:

1. **Fast POC (this repository)** - Building a minimal social network from scratch for rapid prototyping and proof of concept
   - Quick iterations and experimentation
   - Demonstrates core diversity scoring algorithm
   - Simple Flask-based implementation
   - Perfect for testing ideas and gathering feedback

2. **Long-term solution** - Building on top of Diaspora (separate track)
   - Leveraging mature, battle-tested federated social network
   - Full feature set (profiles, privacy, federation, etc.)
   - AGPL-3.0 open source
   - Production-ready infrastructure

This POC serves as a testbed for the diversity scoring concepts before integrating them into a full-featured platform.

### Core Concept

- Each user gets a political profile in three dimensions:
  - Right ↔ Left
  - Liberal ↔ Conservative
  - Religious ↔ Atheist
  - Vegan ↔ Carnivore

- The profile updates dynamically based on the user's reactions

- Posts and comments receive a **Diversity Score** calculated by the variance in profiles of those reacting

- Content that receives positive reactions from a wide variety of camps = high score

### Features

✅ Posts and comments  
✅ 6 reaction types: 👍 Like, ❤️ Love, 😠 Angry, 😂 Laugh, 🤔 Interested, 🤗 Empathy  
✅ Automatic user profile calculation  
✅ Ranking by diversity score  
✅ Simple UI with English/Hebrew toggle  


![Screenshot POC - Bridge Demo.png](Screenshot%20POC%20-%20Bridge%20Demo.png)

![Screenshot - Political Spectrum Distribution.png](Screenshot%20-%20Political%20Spectrum%20Distribution.png)

### How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Then open: **http://localhost:5000**

#### Access a running instance
There is a live instance running on:
http://46.101.134.165:5000/
feel free to visit it

### How Does It Work?

1. **Start**: Each user begins with a random profile in the three dimensions

2. **Learning**: When a user reacts positively (👍❤️🤔🤗) to a post/comment, their profile shifts toward the content author's profile

3. **Diversity Calculation**: 
   - The system checks who reacted to each post/comment
   - Calculates the variance in the profiles of those reacting
   - More variance = higher diversity score

4. **Ranking**: Posts and comments are displayed in order of diversity score (highest first)

### Usage Examples

**Scenario 1: Consensus Post**
- Post: "Hello everyone!"
- 5 right-wing users react 👍
- Diversity score: **Low** (no variance)

**Scenario 2: Bridging Post**
- Post: "Let's talk about the economy"
- 3 right-wing users react 👍
- 3 left-wing users react 🤔
- 2 centrist users react ❤️
- Diversity score: **High** (wide variance)

### POC Limitations

⚠️ This is just a POC! In reality you'd need:
- More sophisticated algorithm for political analysis
- Account for reaction type (angry ≠ love)
- Manipulation prevention
- ML for actual camp identification
- Database persistence

### Possible Extensions

1. **Text Analysis**: Use NLP to automatically identify political leanings from content
2. **Reaction Weights**: Negative reactions (😠) should have different effects
3. **Personalization**: Each user can choose which dimensions matter to them
4. **Prediction**: Predict which content will get high diversity scores
5. **Visualization**: Graphical display of reactor distribution

### Additional Ideas

- **"Bridges"**: Identify users who react positively to content from different camps
- **"Echo"**: Warn when a user is only in a bubble of similar opinions
- **"Healthy Debate"**: Identify discussions with diverse opinions but respectful tone

---

<a name="hebrew"></a>
## עברית

### מה זה?

מערכת בסיסית שמדרגת תוכן לפי **שונות** במחנות של המגיבים, במקום רק לפי כמות הלייקים.

### גישת הפיתוח

אנחנו עובדים בשני כיוונים במקביל:

1. **POC מהיר (הריפוזיטורי הזה)** - בניית רשת חברתית מינימלית מאפס לצורך הדגמה והוכחת היתכנות
   - איטרציות מהירות וניסויים
   - הדגמה של אלגוריתם ציון הגיוון המרכזי
   - מימוש פשוט מבוסס Flask
   - מושלם לבדיקת רעיונות ואיסוף פידבק

2. **פתרון לטווח ארוך** - בנייה על גבי Diaspora (מסלול נפרד)
   - ניצול של רשת חברתית מבוזרת בוגרת ומוכחת
   - סט תכונות מלא (פרופילים, פרטיות, פדרציה וכו')
   - קוד פתוח AGPL-3.0
   - תשתית מוכנה לייצור

ה-POC הזה משמש כמעבדה לבדיקת מושגי ציון הגיוון לפני שילובם בפלטפורמה מלאה.

### הרעיון המרכזי

- כל משתמש מקבל פרופיל פוליטי בשלושה ממדים:
  - ימין ↔ שמאל
  - ליברלי ↔ שמרן
  - אתאיסט ↔ דתי/מאמין
  - טבעוני ↔ קרניבור

- הפרופיל מתעדכן באופן דינמי על בסיס הריאקציות של המשתמש

- פוסטים ותגובות מקבלים **ציון גיוון** שמחושב לפי השונות בפרופילים של המגיבים

- תוכן שמקבל ריאקציות חיוביות ממגוון רחב של מחנות = ציון גבוה

### תכונות

✅ פוסטים ותגובות  
✅ 6 סוגי ריאקציות: 👍 אהבתי, ❤️ אוהב, 😠 כועס, 😂 צוחק, 🤔 מעניין, 🤗 אמפתיה  
✅ חישוב אוטומטי של פרופיל משתמש  
✅ דירוג לפי ציון גיוון  
✅ ממשק משתמש עם מעבר אנגלית/עברית  

### איך להריץ

```bash
# התקנת dependencies
pip install -r requirements.txt

# הרצה
python app.py
```

הגש ל: **http://localhost:5000**

### איך זה עובד?

1. **התחלה**: כל משתמש מתחיל עם פרופיל אקראי בשלושת הממדים

2. **למידה**: כשמשתמש מגיב חיוביות (👍❤️🤔🤗) על פוסט/תגובה, הפרופיל שלו זז לכיוון הפרופיל של מחבר התוכן

3. **חישוב גיוון**: 
   - המערכת בודקת מי הגיב על כל פוסט/תגובה
   - מחשבת את ה-variance בפרופילים של המגיבים
   - ככל שיש יותר שונות = ציון גיוון גבוה יותר

4. **דירוג**: פוסטים ותגובות מוצגים לפי סדר ציון הגיוון (מהגבוה לנמוך)

### דוגמאות לשימוש

**תרחיש 1: פוסט קונצנזוס**
- פוסט: "שלום לכולם!"
- 5 משתמשים ימניים מגיבים 👍
- ציון גיוון: **נמוך** (אין שונות)

**תרחיש 2: פוסט מגשר**
- פוסט: "בואו נדבר על הכלכלה"
- 3 משתמשים ימניים מגיבים 👍
- 3 משתמשים שמאליים מגיבים 🤔
- 2 משתמשים מרכז מגיבים ❤️
- ציון גיוון: **גבוה** (שונות רחבה)

### מגבלות ה-POC

⚠️ זה POC בלבד! במציאות צריך:
- אלגוריתם מתוחכם יותר לניתוח פוליטי
- התייחסות לסוג הריאקציה (כועס ≠ אוהב)
- מניעת מניפולציות
- ML לזיהוי אמיתי של מחנות
- שמירה במסד נתונים

### הרחבות אפשריות

1. **ניתוח טקסט**: שימוש ב-NLP לזיהוי אוטומטי של נטיות פוליטיות מהתוכן
2. **משקלות לריאקציות**: ריאקציה שלילית (😠) צריכה להשפיע אחרת
3. **התאמה אישית**: כל משתמש יכול לבחור אילו ממדים חשובים לו
4. **חיזוי**: חיזוי מראש איזה תוכן יקבל ציון גיוון גבוה
5. **ויזואליזציה**: הצגה גרפית של התפלגות המגיבים

### רעיונות נוספים

- **"גשרים"**: זיהוי משתמשים שמגיבים באופן חיובי על תוכן ממחנות שונים
- **"הד"**: אזהרה כשמשתמש נמצא רק בבועה של דעות דומות
- **"ויכוח בריא"**: זיהוי דיונים שבהם יש מגוון דעות אבל הטון נשאר מכבד
