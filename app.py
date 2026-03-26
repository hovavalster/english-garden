import streamlit as st
import streamlit.components.v1 as components
import subprocess
import io
import base64
import tempfile
import os
import json
import platform
import hashlib
import random
import numpy as np
import soundfile as sf
from pathlib import Path
from datetime import date
from difflib import SequenceMatcher
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="English Garden", page_icon="🌿", layout="centered")

# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM DETECTION
# ══════════════════════════════════════════════════════════════════════════════
IS_WINDOWS = platform.system() == "Windows"
AUDIO_MIME  = "audio/wav" if IS_WINDOWS else "audio/mpeg"

# ══════════════════════════════════════════════════════════════════════════════
# WORD LISTS
# ══════════════════════════════════════════════════════════════════════════════
ANIMALS = [
    {"text": "cat",      "emoji": "🐱"},
    {"text": "dog",      "emoji": "🐶"},
    {"text": "bird",     "emoji": "🐦"},
    {"text": "fish",     "emoji": "🐟"},
    {"text": "cow",      "emoji": "🐄"},
    {"text": "pig",      "emoji": "🐷"},
    {"text": "duck",     "emoji": "🦆"},
    {"text": "bee",      "emoji": "🐝"},
    {"text": "frog",     "emoji": "🐸"},
    {"text": "lion",     "emoji": "🦁"},
    {"text": "bear",     "emoji": "🐻"},
    {"text": "rabbit",   "emoji": "🐰"},
    {"text": "elephant", "emoji": "🐘"},
    {"text": "horse",    "emoji": "🐴"},
    {"text": "monkey",   "emoji": "🐵"},
    {"text": "tiger",    "emoji": "🐯"},
    {"text": "sheep",    "emoji": "🐑"},
    {"text": "turtle",   "emoji": "🐢"},
    {"text": "penguin",  "emoji": "🐧"},
]
KITCHEN = [
    {"text": "cup",    "emoji": "☕"},
    {"text": "spoon",  "emoji": "🥄"},
    {"text": "fork",   "emoji": "🍴"},
    {"text": "plate",  "emoji": "🍽️"},
    {"text": "bowl",   "emoji": "🥣"},
    {"text": "pot",    "emoji": "🍲"},
    {"text": "knife",  "emoji": "🔪"},
    {"text": "glass",  "emoji": "🥤"},
    {"text": "sink",   "emoji": "🚰"},
    {"text": "oven",   "emoji": "🫕"},
    {"text": "fridge", "emoji": "🧊"},
    {"text": "bread",  "emoji": "🍞"},
    {"text": "milk",   "emoji": "🥛"},
    {"text": "egg",    "emoji": "🥚"},
    {"text": "apple",  "emoji": "🍎"},
]
BEDROOM = [
    {"text": "bed",     "emoji": "🛏️"},
    {"text": "pillow",  "emoji": "😴"},
    {"text": "blanket", "emoji": "🛌"},
    {"text": "lamp",    "emoji": "💡"},
    {"text": "door",    "emoji": "🚪"},
    {"text": "window",  "emoji": "🪟"},
    {"text": "chair",   "emoji": "🪑"},
    {"text": "mirror",  "emoji": "🪞"},
    {"text": "clock",   "emoji": "⏰"},
    {"text": "book",    "emoji": "📖"},
    {"text": "toy",     "emoji": "🧸"},
    {"text": "sock",    "emoji": "🧦"},
    {"text": "shoe",    "emoji": "👟"},
]
COLORS = [
    {"text": "red",    "emoji": "🔴"},
    {"text": "blue",   "emoji": "🔵"},
    {"text": "green",  "emoji": "🟢"},
    {"text": "yellow", "emoji": "🟡"},
    {"text": "pink",   "emoji": "🩷"},
    {"text": "purple", "emoji": "🟣"},
    {"text": "orange", "emoji": "🟠"},
    {"text": "white",  "emoji": "⬜"},
    {"text": "black",  "emoji": "⬛"},
    {"text": "brown",  "emoji": "🟫"},
]
NUMBERS = [
    {"text": "one",   "emoji": "1️⃣"},
    {"text": "two",   "emoji": "2️⃣"},
    {"text": "three", "emoji": "3️⃣"},
    {"text": "four",  "emoji": "4️⃣"},
    {"text": "five",  "emoji": "5️⃣"},
    {"text": "six",   "emoji": "6️⃣"},
    {"text": "seven", "emoji": "7️⃣"},
    {"text": "eight", "emoji": "8️⃣"},
    {"text": "nine",  "emoji": "9️⃣"},
    {"text": "ten",   "emoji": "🔟"},
]
BODY_PARTS = [
    {"text": "eye",    "emoji": "👁️"},
    {"text": "ear",    "emoji": "👂"},
    {"text": "nose",   "emoji": "👃"},
    {"text": "mouth",  "emoji": "👄"},
    {"text": "hand",   "emoji": "✋"},
    {"text": "foot",   "emoji": "🦶"},
    {"text": "hair",   "emoji": "💇"},
    {"text": "arm",    "emoji": "💪"},
    {"text": "leg",    "emoji": "🦵"},
    {"text": "finger", "emoji": "☝️"},
]
EMOTIONS = [
    {"text": "happy",     "emoji": "😊"},
    {"text": "sad",       "emoji": "😢"},
    {"text": "angry",     "emoji": "😠"},
    {"text": "scared",    "emoji": "😨"},
    {"text": "surprised", "emoji": "😲"},
    {"text": "tired",     "emoji": "😴"},
    {"text": "excited",   "emoji": "🤩"},
    {"text": "silly",     "emoji": "🤪"},
    {"text": "proud",     "emoji": "😤"},
    {"text": "love",      "emoji": "🥰"},
]
FRUITS = [
    {"text": "apple",      "emoji": "🍎"},
    {"text": "banana",     "emoji": "🍌"},
    {"text": "orange",     "emoji": "🍊"},
    {"text": "strawberry", "emoji": "🍓"},
    {"text": "grape",      "emoji": "🍇"},
    {"text": "mango",      "emoji": "🥭"},
    {"text": "pear",       "emoji": "🍐"},
    {"text": "watermelon", "emoji": "🍉"},
    {"text": "cherry",     "emoji": "🍒"},
    {"text": "lemon",      "emoji": "🍋"},
]
CLOTHES = [
    {"text": "shirt",   "emoji": "👕"},
    {"text": "pants",   "emoji": "👖"},
    {"text": "dress",   "emoji": "👗"},
    {"text": "shoe",    "emoji": "👟"},
    {"text": "hat",     "emoji": "🎩"},
    {"text": "socks",   "emoji": "🧦"},
    {"text": "jacket",  "emoji": "🧥"},
    {"text": "gloves",  "emoji": "🧤"},
    {"text": "scarf",   "emoji": "🧣"},
    {"text": "boots",   "emoji": "👢"},
]
VEHICLES = [
    {"text": "car",        "emoji": "🚗"},
    {"text": "bus",        "emoji": "🚌"},
    {"text": "train",      "emoji": "🚂"},
    {"text": "plane",      "emoji": "✈️"},
    {"text": "bike",       "emoji": "🚲"},
    {"text": "truck",      "emoji": "🚚"},
    {"text": "boat",       "emoji": "⛵"},
    {"text": "rocket",     "emoji": "🚀"},
    {"text": "helicopter", "emoji": "🚁"},
    {"text": "tractor",    "emoji": "🚜"},
    {"text": "taxi",       "emoji": "🚕"},
    {"text": "fire truck", "emoji": "🚒"},
]
WEATHER = [
    {"text": "sun",      "emoji": "☀️"},
    {"text": "rain",     "emoji": "🌧️"},
    {"text": "snow",     "emoji": "❄️"},
    {"text": "cloud",    "emoji": "☁️"},
    {"text": "rainbow",  "emoji": "🌈"},
    {"text": "wind",     "emoji": "💨"},
    {"text": "thunder",  "emoji": "⛈️"},
    {"text": "fog",      "emoji": "🌫️"},
    {"text": "hot",      "emoji": "🥵"},
    {"text": "cold",     "emoji": "🥶"},
    {"text": "storm",    "emoji": "🌪️"},
]
EASY_PHRASES = [
    {"text": "Hello",        "emoji": "👋"},
    {"text": "Bye bye",      "emoji": "👋"},
    {"text": "Thank you",    "emoji": "🙏"},
    {"text": "Yes please",   "emoji": "✅"},
    {"text": "No thank you", "emoji": "🙅"},
    {"text": "I love you",   "emoji": "❤️"},
    {"text": "Good morning", "emoji": "☀️"},
    {"text": "Good night",   "emoji": "🌙"},
    {"text": "More please",  "emoji": "🍽️"},
    {"text": "I am happy",   "emoji": "😊"},
    {"text": "I am hungry",  "emoji": "🍔"},
    {"text": "Let us go",    "emoji": "🚶"},
    {"text": "Come here",    "emoji": "🫸"},
    {"text": "I am tired",   "emoji": "😴"},
    {"text": "Help me",      "emoji": "🙋"},
    {"text": "Look at me",   "emoji": "👀"},
]
SENTENCES = [
    {"text": "I love you so much",              "emoji": "❤️"},
    {"text": "Good morning my dear friend",     "emoji": "☀️"},
    {"text": "Good night sleep tight",          "emoji": "🌙"},
    {"text": "Thank you very much",             "emoji": "🙏"},
    {"text": "I am very happy today",           "emoji": "😊"},
    {"text": "I am hungry can we eat",          "emoji": "🍽️"},
    {"text": "I am tired and want to sleep",    "emoji": "😴"},
    {"text": "Can we please go play now",       "emoji": "🎮"},
    {"text": "Can I have some water please",    "emoji": "💧"},
    {"text": "You are so very nice",            "emoji": "🌟"},
    {"text": "I want to go outside now",        "emoji": "🌳"},
    {"text": "Please read me a book",           "emoji": "📖"},
    {"text": "I want a big warm hug",           "emoji": "🤗"},
    {"text": "The sun is shining today",        "emoji": "🌞"},
    {"text": "I see a pretty butterfly",        "emoji": "🦋"},
    {"text": "Can you help me please",          "emoji": "🙋"},
    {"text": "I like to play with you",         "emoji": "🫶"},
    {"text": "The dog is so cute",              "emoji": "🐶"},
    {"text": "Let us go to the park",           "emoji": "🌿"},
    {"text": "I love to eat apples",            "emoji": "🍎"},
    {"text": "Can we bake some cookies",        "emoji": "🍪"},
    {"text": "I want to play with my toys",     "emoji": "🧸"},
    {"text": "Look at the pretty rainbow",      "emoji": "🌈"},
    {"text": "I love my family so much",        "emoji": "👨‍👩‍👧"},
    {"text": "Can we watch a movie together",   "emoji": "🎬"},
    {"text": "I want to dance and sing",        "emoji": "🎵"},
    {"text": "The kitty is soft and fluffy",    "emoji": "🐱"},
    {"text": "We are going to the beach",       "emoji": "🏖️"},
    {"text": "I love to jump and run",          "emoji": "🏃"},
    {"text": "The bird is singing in the tree", "emoji": "🐦"},
    {"text": "I found a shiny little star",     "emoji": "⭐"},
    {"text": "Can I have a cookie please",      "emoji": "🍪"},
    {"text": "I see a big fluffy cloud",        "emoji": "☁️"},
    {"text": "Let us pick some flowers",        "emoji": "🌸"},
    {"text": "I like the smell of rain",        "emoji": "🌧️"},
]

ALL_CATEGORIES = {
    "🐾 Animals":     ANIMALS,
    "🍳 Kitchen":     KITCHEN,
    "🛏️ Bedroom":     BEDROOM,
    "🎨 Colors":      COLORS,
    "🔢 Numbers":     NUMBERS,
    "👁️ Body Parts":  BODY_PARTS,
    "😊 Emotions":    EMOTIONS,
    "🍓 Fruits":      FRUITS,
    "👕 Clothes":     CLOTHES,
    "🚗 Vehicles":    VEHICLES,
    "🌦️ Weather":     WEATHER,
    "💬 Easy Phrases": EASY_PHRASES,
    "📝 Sentences":   SENTENCES,
}

# ══════════════════════════════════════════════════════════════════════════════
# STORIES
# ══════════════════════════════════════════════════════════════════════════════
STORY_CATERPILLAR = [
    {"text": "egg",         "emoji": "🥚",  "scene": "🍃🍃🍃",
     "narration": "Once upon a time, on a warm sunny leaf...\nthere was one tiny, round egg.",
     "praise": "Yes! A tiny egg, waiting to hatch!"},
    {"text": "caterpillar", "emoji": "🐛",  "scene": "🌿🌿🌿",
     "narration": "One morning — POP! The egg cracked open.\nOut crawled a tiny, hungry caterpillar!",
     "praise": "Hello, little caterpillar! 🐛"},
    {"text": "apple",       "emoji": "🍎",  "scene": "🌳🌳🌳",
     "narration": "On Monday she was so hungry.\nShe found one big, juicy apple... crunch!",
     "praise": "Mmm! A delicious apple!"},
    {"text": "pear",        "emoji": "🍐",  "scene": "🌿✨🌿",
     "narration": "On Tuesday she found two soft, green pears.\nShe ate them both — every single bite!",
     "praise": "Two sweet pears! She's growing!"},
    {"text": "strawberry",  "emoji": "🍓",  "scene": "🌸🌸🌸",
     "narration": "On Wednesday she nibbled three little strawberries.\nThey were sweet and red and perfect.",
     "praise": "Strawberries! Her favourite! 🍓"},
    {"text": "leaf",        "emoji": "🍃",  "scene": "🍂🍃🍂",
     "narration": "She was very, very full.\nShe found one big green leaf and wrapped herself inside.\nTime to sleep and dream...",
     "praise": "Goodnight, little caterpillar! 😴"},
    {"text": "butterfly",   "emoji": "🦋",  "scene": "🌺🌸🌺",
     "narration": "Two weeks later... something magical happened! ✨\nThe leaf opened and out flew...\na beautiful butterfly!",
     "praise": "🎉 She did it! A beautiful butterfly! 🎉", "final": True},
]

STORY_GARDEN = [
    {"text": "seed",    "emoji": "🌰",  "scene": "🌍🌍🌍",
     "narration": "In the garden, on a warm spring day,\nwe planted one tiny seed in the ground.",
     "praise": "The seed is sleeping in the earth!"},
    {"text": "water",   "emoji": "💧",  "scene": "🌧️🌧️🌧️",
     "narration": "We gave it water every morning.\nDrip, drip, drip...",
     "praise": "Water! The seed is drinking! 💧"},
    {"text": "sun",     "emoji": "☀️",  "scene": "🌤️🌤️🌤️",
     "narration": "The warm sun shone down.\nSomething was waking up underground!",
     "praise": "The sun gives energy! ☀️"},
    {"text": "sprout",  "emoji": "🌱",  "scene": "🌿🌿🌿",
     "narration": "One morning — a tiny green sprout\npoked up through the soil! Hello!",
     "praise": "A sprout! It's alive! 🌱"},
    {"text": "tree",    "emoji": "🌳",  "scene": "🌲🌳🌲",
     "narration": "Days passed... weeks passed...\nThe little sprout grew into a tall, strong tree!",
     "praise": "A beautiful tree! 🌳"},
    {"text": "flower",  "emoji": "🌸",  "scene": "🌺🌸🌻",
     "narration": "And then... the most beautiful thing happened.\nColourful flowers bloomed everywhere! 🌸",
     "praise": "🎉 The garden is blooming! 🌸", "final": True},
]

STORY_FARM = [
    {"text": "egg",     "emoji": "🥚",  "scene": "🌾🌾🌾",
     "narration": "On the farm, in a warm cozy nest,\nthere sat a round, speckled egg.",
     "praise": "A little egg on the farm!"},
    {"text": "nest",    "emoji": "🪺",  "scene": "🌿🌿🌿",
     "narration": "The egg sat snug in a soft nest,\nmade of hay and feathers.",
     "praise": "A cozy nest! 🪺"},
    {"text": "crack",   "emoji": "🐣",  "scene": "✨✨✨",
     "narration": "Tap tap tap... CRACK!\nA tiny yellow beak poked through the shell!",
     "praise": "The egg is hatching! 🐣"},
    {"text": "chick",   "emoji": "🐥",  "scene": "☀️🌾☀️",
     "narration": "Out jumped a fluffy yellow chick,\nblinked its eyes, and said: Cheep cheep!",
     "praise": "Hello, little chick! 🐥"},
    {"text": "grass",   "emoji": "🌾",  "scene": "🌿🌾🌿",
     "narration": "The chick ran through the green grass,\npecking at seeds and exploring the farm.",
     "praise": "The chick loves the grass! 🌾"},
    {"text": "hen",     "emoji": "🐓",  "scene": "🏡🌾🏡",
     "narration": "The chick grew and grew...\nuntil one day, it was a big proud hen!",
     "praise": "🎉 The chick became a hen! 🐓", "final": True},
]

STORY_OCEAN = [
    {"text": "cloud",  "emoji": "☁️",  "scene": "🌤️🌤️🌤️",
     "narration": "High up in the sky,\na fluffy cloud was filled with water.",
     "praise": "A big cloud full of water! ☁️"},
    {"text": "rain",   "emoji": "🌧️",  "scene": "⛈️⛈️⛈️",
     "narration": "Pitter patter! The cloud let go\nand rain fell down, down, down.",
     "praise": "The rain is falling! 🌧️"},
    {"text": "river",  "emoji": "🏞️",  "scene": "🌊🌿🌊",
     "narration": "The raindrops joined together\nand flowed into a winding river.",
     "praise": "A beautiful river! 🏞️"},
    {"text": "wave",   "emoji": "🌊",  "scene": "🌊🌊🌊",
     "narration": "The river flowed and flowed\nuntil it reached the crashing waves!",
     "praise": "Big waves! 🌊"},
    {"text": "fish",   "emoji": "🐠",  "scene": "🐠🌊🐠",
     "narration": "Under the waves, colourful fish\nswam and played in the deep blue sea.",
     "praise": "Beautiful fish! 🐠"},
    {"text": "ocean",  "emoji": "🌊",  "scene": "🌅🌊🌅",
     "narration": "And there it was — the vast, sparkling ocean!\nThe water's long, long journey was complete. 🌅",
     "praise": "🎉 The ocean! The journey is complete! 🌊", "final": True},
]

STORY_SLEEP = [
    {"text": "sun",     "emoji": "☀️",  "scene": "🌞🌤️🌞",
     "narration": "It was a bright, sunny morning.\nThe day was just beginning!",
     "praise": "Good morning, sunshine! ☀️"},
    {"text": "play",    "emoji": "🎮",  "scene": "🌳🌿🌳",
     "narration": "We played and ran and laughed all day,\nin the garden, in the park, everywhere!",
     "praise": "So much fun! 🎮"},
    {"text": "bath",    "emoji": "🛁",  "scene": "🫧🛁🫧",
     "narration": "As the sun began to set,\nit was time for a warm, bubbly bath.",
     "praise": "Clean and cozy! 🛁"},
    {"text": "pajamas", "emoji": "🩲",  "scene": "🌙✨🌙",
     "narration": "We put on our soft, warm pajamas,\nready for a good night's sleep.",
     "praise": "Cozy pajamas! 🩲"},
    {"text": "bed",     "emoji": "🛏️",  "scene": "🌙💫🌙",
     "narration": "We climbed into our cozy, warm bed,\nand pulled the blanket up tight.",
     "praise": "Into bed we go! 🛏️"},
    {"text": "dream",   "emoji": "💤",  "scene": "⭐🌙⭐",
     "narration": "Eyes closed... breathing slowed...\nand beautiful dreams began. 💫",
     "praise": "🎉 Sweet dreams! Goodnight! 💤", "final": True},
]

STORY_BIRTHDAY = [
    {"text": "cake",    "emoji": "🎂",  "scene": "🎈🎂🎈",
     "narration": "Today is your birthday! 🎉\nThere is a big, beautiful cake waiting for you!",
     "praise": "A yummy birthday cake! 🎂"},
    {"text": "candles", "emoji": "🕯️",  "scene": "✨🕯️✨",
     "narration": "We put five little candles on the cake.\nOne... two... three... four... five!",
     "praise": "So many candles! 🕯️"},
    {"text": "wish",    "emoji": "⭐",  "scene": "⭐💫⭐",
     "narration": "Close your eyes and make a secret wish...\nShhh, don't tell anyone!",
     "praise": "Your wish is coming true! ⭐"},
    {"text": "blow",    "emoji": "💨",  "scene": "🕯️💨🕯️",
     "narration": "Take a big, deep breath...\nNow BLOW out all the candles!",
     "praise": "You blew them all out! 💨"},
    {"text": "friends", "emoji": "👧",  "scene": "👧👦👶",
     "narration": "All your friends come running in!\nThey shout: Surprise! We love you!",
     "praise": "Your friends are here! 🎉"},
    {"text": "happy",   "emoji": "🥳",  "scene": "🎉🥳🎉",
     "narration": "Everyone sings: Happy Birthday to you! 🎵\nIt is the most wonderful day ever!",
     "praise": "🎉 Happy Birthday! 🥳", "final": True},
]

STORY_SPACE = [
    {"text": "stars",   "emoji": "⭐",  "scene": "🌌⭐🌌",
     "narration": "Look up at the night sky!\nSo many beautiful, twinkling stars!",
     "praise": "Stars! So many stars! ⭐"},
    {"text": "moon",    "emoji": "🌕",  "scene": "🌙✨🌙",
     "narration": "The big round moon is glowing bright.\nIt lights up the whole dark sky.",
     "praise": "The beautiful moon! 🌕"},
    {"text": "rocket",  "emoji": "🚀",  "scene": "🚀💨🚀",
     "narration": "WHOOOOSH! A rocket blasts off!\n3... 2... 1... BLAST OFF! 🚀",
     "praise": "The rocket is flying! 🚀"},
    {"text": "planet",  "emoji": "🪐",  "scene": "🪐⭐🪐",
     "narration": "The rocket flies past a giant planet\nwith beautiful colourful rings around it!",
     "praise": "A beautiful planet! 🪐"},
    {"text": "alien",   "emoji": "👽",  "scene": "🛸👽🛸",
     "narration": "Suddenly... a little green alien\nwaves hello from a tiny spaceship!",
     "praise": "A friendly alien! 👽"},
    {"text": "earth",   "emoji": "🌍",  "scene": "🌍💫🌍",
     "narration": "Time to fly back home.\nThere it is — our beautiful blue Earth! 🌍",
     "praise": "🎉 We're home! Our beautiful Earth! 🌍", "final": True},
]

ALL_STORIES = {
    "caterpillar": (STORY_CATERPILLAR, "🐛 Caterpillar"),
    "garden":      (STORY_GARDEN,      "🌱 Garden"),
    "farm":        (STORY_FARM,        "🐣 Farm"),
    "ocean":       (STORY_OCEAN,       "🌊 Ocean"),
    "sleep":       (STORY_SLEEP,       "🌙 Bedtime"),
    "birthday":    (STORY_BIRTHDAY,    "🎂 Birthday"),
    "space":       (STORY_SPACE,       "🚀 Space"),
}

# Per-story card background gradient and accent color
STORY_COLORS = {
    "caterpillar": ("linear-gradient(160deg, #F1FFF4 0%, #D6F5DF 100%)", "#2E7D32"),
    "garden":      ("linear-gradient(160deg, #F9FFE8 0%, #E8F5C8 100%)", "#558B2F"),
    "farm":        ("linear-gradient(160deg, #FFFEF0 0%, #FFF3B0 100%)", "#F57F17"),
    "ocean":       ("linear-gradient(160deg, #EFF8FF 0%, #CCE8FF 100%)", "#0277BD"),
    "sleep":       ("linear-gradient(160deg, #F5F0FF 0%, #E4D8F8 100%)", "#6A1B9A"),
    "birthday":    ("linear-gradient(160deg, #FFF0F8 0%, #FFD6E8 100%)", "#AD1457"),
    "space":       ("linear-gradient(160deg, #F0EEFF 0%, #DDD8F8 100%)", "#283593"),
}

# ══════════════════════════════════════════════════════════════════════════════
# BADGES
# ══════════════════════════════════════════════════════════════════════════════
BADGES = [
    {"key": "first_star",   "label": "🌟 First Star",    "desc": "Got your first word right!",    "type": "total_correct",     "value": 1},
    {"key": "five_right",   "label": "🎯 Sharp Shooter", "desc": "5 correct answers!",            "type": "total_correct",     "value": 5},
    {"key": "twenty_five",  "label": "🦋 Butterfly",     "desc": "25 correct answers!",           "type": "total_correct",     "value": 25},
    {"key": "champion",     "label": "🏆 Champion",      "desc": "100 correct answers!",          "type": "total_correct",     "value": 100},
    {"key": "story_teller", "label": "📖 Story Teller",  "desc": "Completed a story!",            "type": "stories_completed", "value": 1},
    {"key": "all_stories",  "label": "✨ Story Master",  "desc": "Completed all 5 stories!",      "type": "stories_completed", "value": 5},
    {"key": "streak_3",     "label": "🔥 On Fire",       "desc": "3 days in a row!",              "type": "streak_days",       "value": 3},
    {"key": "streak_7",     "label": "💫 Week Warrior",  "desc": "7 days in a row!",              "type": "streak_days",       "value": 7},
    {"key": "word_maker",   "label": "🎨 Word Maker",    "desc": "Added a custom word!",          "type": "custom_words",      "value": 1},
]

# ══════════════════════════════════════════════════════════════════════════════
# PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════
DATA_DIR  = Path(__file__).parent / "data"
PROG_FILE = DATA_DIR / "progress.json"


def default_progress():
    return {
        "child_name": None,
        "last_played": None,
        "streak_days": 0,
        "total_correct": 0,
        "badges_earned": [],
        "word_stats": {},
        "category_stats": {},
        "difficulty_level": 1,
        "custom_words": [],
        "stories_completed": [],
    }


def load_progress():
    if PROG_FILE.exists():
        try:
            return json.loads(PROG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default_progress()


def save_progress(p):
    DATA_DIR.mkdir(exist_ok=True)
    PROG_FILE.write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")


def update_streak(p):
    today_str = date.today().isoformat()
    last = p.get("last_played")
    if last == today_str:
        return p
    if last:
        from datetime import datetime
        delta = (datetime.fromisoformat(today_str) - datetime.fromisoformat(last)).days
        p["streak_days"] = p.get("streak_days", 0) + 1 if delta == 1 else 1
    else:
        p["streak_days"] = 1
    p["last_played"] = today_str
    return p


def record_answer(word_text, category, correct):
    p = st.session_state.progress
    ws = p.setdefault("word_stats", {})
    wentry = ws.setdefault(word_text, {"correct": 0, "wrong": 0})
    wentry["correct" if correct else "wrong"] += 1
    cs = p.setdefault("category_stats", {})
    centry = cs.setdefault(category, {"correct": 0, "wrong": 0})
    centry["correct" if correct else "wrong"] += 1
    if correct:
        p["total_correct"] = p.get("total_correct", 0) + 1
    st.session_state.progress_dirty = True


def flush_progress():
    if st.session_state.get("progress_dirty"):
        save_progress(st.session_state.progress)
        st.session_state.progress_dirty = False


def check_badges(p):
    earned = p.get("badges_earned", [])
    new_badges = []
    for b in BADGES:
        if b["key"] in earned:
            continue
        btype, bval = b["type"], b["value"]
        if btype == "total_correct" and p.get("total_correct", 0) >= bval:
            earned.append(b["key"]); new_badges.append(b)
        elif btype == "stories_completed" and len(p.get("stories_completed", [])) >= bval:
            earned.append(b["key"]); new_badges.append(b)
        elif btype == "streak_days" and p.get("streak_days", 0) >= bval:
            earned.append(b["key"]); new_badges.append(b)
        elif btype == "custom_words" and len(p.get("custom_words", [])) >= bval:
            earned.append(b["key"]); new_badges.append(b)
    p["badges_earned"] = earned
    if new_badges:
        st.session_state.progress_dirty = True
    return new_badges


def get_all_categories():
    cats = dict(ALL_CATEGORIES)
    cw = st.session_state.get("progress", {}).get("custom_words", [])
    if cw:
        cats["📝 My Words"] = cw
    return cats


def get_word_of_the_day():
    name = st.session_state.get("child_name") or "friend"
    today_str = date.today().isoformat()
    all_words = [w for wl in ALL_CATEGORIES.values() for w in wl]
    idx = int(hashlib.md5(f"{today_str}{name}".encode()).hexdigest(), 16) % len(all_words)
    return all_words[idx]


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO — TTS
# ══════════════════════════════════════════════════════════════════════════════
def _speak_edge(text, voice="en-US-AnaNeural"):
    """Microsoft Edge neural TTS — natural child voice, free, needs internet."""
    import asyncio
    import threading
    import edge_tts

    result = [None]

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        buf = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
        result[0] = buf.getvalue()

    def _thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_run())
        finally:
            loop.close()

    t = threading.Thread(target=_thread)
    t.start()
    t.join(timeout=15)
    return result[0]  # mp3 bytes, or None on failure


def _speak_gtts(text):
    from gtts import gTTS
    buf = io.BytesIO()
    gTTS(text=text, lang="en", slow=True).write_to_fp(buf)
    return buf.getvalue()


def _speak_windows_sapi(text):
    """Fallback: Windows SAPI (robotic but offline)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_path = tmp.name
    tmp.close()
    safe = text.replace("'", "''")
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = -2; "
        f"$s.SetOutputToWaveFile('{tmp_path}'); "
        f"$s.Speak('{safe}'); "
        "$s.Dispose()"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            capture_output=True, timeout=15,
        )
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@st.cache_data(show_spinner=False)
def speak(text):
    """Returns (audio_bytes, mime_type). Tries Edge neural → gTTS → SAPI."""
    try:
        audio = _speak_edge(text)
        if audio:
            return audio, "audio/mpeg"
    except Exception:
        pass
    try:
        return _speak_gtts(text), "audio/mpeg"
    except Exception:
        pass
    return _speak_windows_sapi(text), "audio/wav"


def autoplay(audio_or_tuple, mime=None):
    if isinstance(audio_or_tuple, tuple):
        audio_bytes, mime = audio_or_tuple
    else:
        audio_bytes = audio_or_tuple
        if mime is None:
            mime = AUDIO_MIME
    st.session_state.setdefault("play_count", 0)
    st.session_state.play_count += 1
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f'<audio autoplay data-n="{st.session_state.play_count}">'
        f'<source src="data:{mime};base64,{b64}" type="{mime}">'
        f'</audio>',
        unsafe_allow_html=True,
    )


def speak_instant(text):
    """Speak text using the browser's built-in speech engine — zero latency."""
    safe = text.replace("\\", "\\\\").replace("'", "\\'")
    js = f"""
    (function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang = 'en-US';
        u.rate = 0.82;
        u.pitch = 1.05;
        function go() {{
            var voices = window.speechSynthesis.getVoices();
            var en = voices.filter(function(v) {{ return v.lang.startsWith('en'); }});
            var pick = en.find(function(v) {{
                return v.name.indexOf('Zira') >= 0 || v.name.indexOf('Aria') >= 0 ||
                       v.name.indexOf('Jenny') >= 0 || v.name.indexOf('Google') >= 0 ||
                       v.name.indexOf('Ana') >= 0;
            }}) || en[0];
            if (pick) u.voice = pick;
            window.speechSynthesis.speak(u);
        }}
        if (window.speechSynthesis.getVoices().length > 0) {{ go(); }}
        else {{ window.speechSynthesis.onvoiceschanged = go; }}
    }})();
    """
    components.html(f"<script>{js}</script>", height=0)


def speak_story_step(narration, word):
    """Speak story narration then the target word after a short pause."""
    safe_nar = narration.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ").replace('"', '\\"')
    safe_word = word.replace("'", "\\'")
    js = f"""
    (function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        function getVoice() {{
            var voices = window.speechSynthesis.getVoices();
            var en = voices.filter(function(v) {{ return v.lang.startsWith('en'); }});
            return en.find(function(v) {{
                return v.name.indexOf('Zira') >= 0 || v.name.indexOf('Aria') >= 0 ||
                       v.name.indexOf('Jenny') >= 0 || v.name.indexOf('Google') >= 0 ||
                       v.name.indexOf('Ana') >= 0;
            }}) || en[0];
        }}
        function speak(text, rate, onEnd) {{
            var u = new SpeechSynthesisUtterance(text);
            u.lang = 'en-US'; u.rate = rate; u.pitch = 1.05;
            var v = getVoice(); if (v) u.voice = v;
            if (onEnd) u.onend = onEnd;
            window.speechSynthesis.speak(u);
        }}
        function go() {{
            speak('{safe_nar}', 0.78, function() {{
                setTimeout(function() {{ speak('{safe_word}', 0.72, null); }}, 500);
            }});
        }}
        if (window.speechSynthesis.getVoices().length > 0) {{ go(); }}
        else {{ window.speechSynthesis.onvoiceschanged = go; }}
    }})();
    """
    components.html(f"<script>{js}</script>", height=0)


def speak_then_record(word):
    """Speak word slowly, show 3-2-1 countdown, then auto-click the mic button."""
    safe = word.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
    components.html(f"""<script>
    (function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        function getVoice() {{
            var vs = window.speechSynthesis.getVoices();
            var en = vs.filter(function(v) {{ return v.lang.startsWith('en'); }});
            return en.find(function(v) {{
                return ['Zira','Aria','Jenny','Google','Ana'].some(function(n) {{ return v.name.indexOf(n) >= 0; }});
            }}) || en[0];
        }}
        function doSpeak() {{
            var u = new SpeechSynthesisUtterance('{safe}');
            u.lang = 'en-US'; u.rate = 0.72; u.pitch = 1.05;
            var v = getVoice(); if (v) u.voice = v;
            u.onend = startCountdown;
            window.speechSynthesis.speak(u);
        }}
        var vs = window.speechSynthesis.getVoices();
        if (vs.length) {{ doSpeak(); }} else {{ window.speechSynthesis.onvoiceschanged = doSpeak; }}

        function startCountdown() {{
            var pd = window.parent.document;
            var existing = pd.getElementById('echo-cd');
            if (existing) existing.remove();
            var ov = pd.createElement('div');
            ov.id = 'echo-cd';
            ov.style.cssText = [
                'position:fixed', 'top:50%', 'left:50%',
                'transform:translate(-50%,-50%)',
                'background:rgba(193,122,74,0.95)',
                'color:white', 'border-radius:40px',
                'padding:28px 64px', 'font-size:80px',
                'font-weight:900', 'z-index:99999',
                'font-family:Nunito,sans-serif',
                'text-align:center', 'min-width:160px',
                'box-shadow:0 8px 40px rgba(0,0,0,0.3)'
            ].join(';');
            pd.body.appendChild(ov);
            var n = 3;
            function tick() {{
                if (n > 0) {{
                    ov.textContent = n--;
                    setTimeout(tick, 750);
                }} else {{
                    ov.textContent = '🎤';
                    setTimeout(function() {{
                        ov.remove();
                        pd.querySelectorAll('iframe').forEach(function(f) {{
                            try {{
                                var btn = f.contentDocument && f.contentDocument.querySelector('button');
                                if (btn) btn.click();
                            }} catch(e) {{}}
                        }});
                    }}, 600);
                }}
            }}
            tick();
        }}
    }})();
    </script>""", height=0)


def animated_scene(scene_str):
    """Wrap each emoji in the scene string in a span with staggered bounce animation."""
    spans = ""
    delay = 0.0
    for ch in scene_str:
        if ch.strip():
            spans += (
                f'<span style="display:inline-block;'
                f'animation:scene-float 2.8s ease-in-out {delay:.2f}s infinite;">'
                f'{ch}</span>'
            )
            delay += 0.25
        else:
            spans += ch
    return spans


def inject_mic_listener():
    """JS that shows a 'Listening...' overlay when the mic button is tapped."""
    components.html("""
    <script>
    (function() {
        function attach() {
            var frames = window.parent.document.querySelectorAll('iframe');
            frames.forEach(function(frame) {
                try {
                    var d = frame.contentDocument;
                    if (!d) return;
                    var btn = d.querySelector('button');
                    if (btn && !btn._gardenAttached) {
                        btn._gardenAttached = true;
                        btn.addEventListener('click', function() {
                            var pd = window.parent.document;
                            var existing = pd.getElementById('mic-listen-ov');
                            if (existing) { existing.remove(); return; }
                            var el = pd.createElement('div');
                            el.id = 'mic-listen-ov';
                            el.style.cssText = [
                                'position:fixed', 'bottom:110px', 'left:50%',
                                'transform:translateX(-50%)',
                                'background:rgba(193,122,74,0.92)', 'color:white',
                                'border-radius:24px', 'padding:14px 32px',
                                'font-size:22px', 'font-weight:800',
                                'z-index:99998', 'font-family:Nunito,sans-serif',
                                'pointer-events:none', 'text-align:center',
                                'box-shadow:0 4px 20px rgba(0,0,0,0.2)'
                            ].join(';');
                            el.innerHTML = '🎤 Listening&hellip; say the word!';
                            pd.body.appendChild(el);
                            setTimeout(function() { if (el.parentNode) el.remove(); }, 5000);
                        });
                    }
                } catch(e) {}
            });
        }
        setTimeout(attach, 400);
        setTimeout(attach, 1200);
    })();
    </script>
    """, height=0)


def show_splash(emoji="🌟", text="Amazing!"):
    """Full-screen celebration overlay for correct answers."""
    js = f"""
    (function() {{
        var d = window.parent.document;
        if (d.getElementById('garden-splash')) return;
        var ov = d.createElement('div');
        ov.id = 'garden-splash';
        ov.style.cssText = 'position:fixed;inset:0;background:rgba(255,245,140,0.93);z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none;';
        ov.innerHTML = '<div style="font-size:130px;line-height:1;animation:sp-pop 0.5s cubic-bezier(0.175,0.885,0.32,1.275) both">{emoji}</div>'
                     + '<div style="font-size:54px;font-weight:900;color:#3D2B1F;font-family:Nunito,sans-serif;margin-top:14px;">{text}</div>';
        var st2 = d.createElement('style');
        st2.textContent = '@keyframes sp-pop{{0%{{transform:scale(0)}}60%{{transform:scale(1.25)}}100%{{transform:scale(1)}}}} @keyframes sp-fade{{0%{{opacity:1}}100%{{opacity:0}}}}';
        d.head.appendChild(st2);
        d.body.appendChild(ov);
        setTimeout(function(){{ov.style.animation='sp-fade 0.4s ease-out forwards';}}, 1300);
        setTimeout(function(){{ov.remove();st2.remove();}}, 1700);
    }})();
    """
    components.html(f"<script>{js}</script>", height=0)


def _truncate_audio(audio_bytes, max_seconds=3):
    """Return audio bytes truncated to at most max_seconds."""
    try:
        arr, sr = sf.read(io.BytesIO(audio_bytes))
        limit = int(max_seconds * sr)
        if len(arr) > limit:
            arr = arr[:limit]
        buf = io.BytesIO()
        sf.write(buf, arr, sr, format="WAV")
        return buf.getvalue()
    except Exception:
        return audio_bytes


def playback_child_voice(audio_bytes):
    """Play the child's own recorded voice back to them (first 3 s only)."""
    audio_bytes = _truncate_audio(audio_bytes, max_seconds=4)
    st.session_state.setdefault("play_count", 0)
    st.session_state.play_count += 1
    b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f'<audio autoplay data-n="v{st.session_state.play_count}">'
        f'<source src="data:audio/wav;base64,{b64}" type="audio/wav">'
        f'<source src="data:audio/webm;base64,{b64}" type="audio/webm">'
        f'</audio>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# AUDIO — SOUND EFFECTS & MUSIC
# ══════════════════════════════════════════════════════════════════════════════
_SOUND_JS = {
    "correct": """
        const ctx=new(window.AudioContext||window.webkitAudioContext)();
        [[523,0,0.12],[659,0.13,0.12],[784,0.26,0.25]].forEach(([f,s,d])=>{
            const o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.frequency.value=f;o.type='sine';
            g.gain.setValueAtTime(0.35,ctx.currentTime+s);
            g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+s+d);
            o.start(ctx.currentTime+s);o.stop(ctx.currentTime+s+d+0.05);
        });
    """,
    "wrong": """
        const ctx=new(window.AudioContext||window.webkitAudioContext)();
        [[400,0,0.18],[320,0.2,0.25]].forEach(([f,s,d])=>{
            const o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.frequency.value=f;o.type='sine';
            g.gain.setValueAtTime(0.25,ctx.currentTime+s);
            g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+s+d);
            o.start(ctx.currentTime+s);o.stop(ctx.currentTime+s+d+0.05);
        });
    """,
    "badge": """
        const ctx=new(window.AudioContext||window.webkitAudioContext)();
        [[523,0,0.1],[659,0.1,0.1],[784,0.2,0.1],[1047,0.3,0.1],[1319,0.4,0.3]].forEach(([f,s,d])=>{
            const o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.frequency.value=f;o.type='sine';
            g.gain.setValueAtTime(0.35,ctx.currentTime+s);
            g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+s+d);
            o.start(ctx.currentTime+s);o.stop(ctx.currentTime+s+d+0.05);
        });
    """,
}


def play_sound(kind):
    js = _SOUND_JS.get(kind, "")
    if js:
        components.html(f"<script>{js}</script>", height=0)


def inject_ambient_music(playing):
    if playing:
        js = """
        if(!window._gardenAudio){
            const ctx=new(window.AudioContext||window.webkitAudioContext)();
            const master=ctx.createGain();master.gain.value=0.04;master.connect(ctx.destination);
            const lfo=ctx.createOscillator();const lfoG=ctx.createGain();
            lfo.frequency.value=0.3;lfoG.gain.value=0.015;
            lfo.connect(lfoG);lfoG.connect(master.gain);lfo.start();
            [220,277,330].forEach(f=>{
                const o=ctx.createOscillator();o.type='sine';o.frequency.value=f;
                o.connect(master);o.start();
            });
            window._gardenAudio=ctx;
        }
        """
    else:
        js = """
        if(window._gardenAudio){window._gardenAudio.close();window._gardenAudio=null;}
        """
    components.html(f"<script>{js}</script>", height=0)


# ══════════════════════════════════════════════════════════════════════════════
# SPEECH RECOGNITION
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Loading speech model (one-time)...")
def load_whisper():
    from faster_whisper import WhisperModel
    return WhisperModel("tiny", device="cpu", compute_type="int8")


def try_recognize(audio_bytes):
    try:
        audio_bytes = _truncate_audio(audio_bytes, max_seconds=4)
        audio_array, sample_rate = sf.read(io.BytesIO(audio_bytes))
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)
        if sample_rate != 16000:
            step = sample_rate / 16000
            indices = np.arange(0, len(audio_array), step).astype(int)
            indices = indices[indices < len(audio_array)]
            audio_array = audio_array[indices]
        audio_array = audio_array.astype(np.float32)
        model = load_whisper()
        segments, _ = model.transcribe(audio_array, language="en", beam_size=1,
                                        vad_filter=True, no_speech_threshold=0.3)
        text = " ".join(s.text.strip() for s in segments).strip()
        return (text, None) if text else (None, "quiet")
    except Exception:
        return None, "error"


# Common mispronunciations for Hebrew-speaking children
# th → d/t/f, r → w/l, long vowels vary
SOUND_ALIASES = {
    "three":   ["free", "tree", "dee", "fee", "dree"],
    "the":     ["da", "de", "duh", "deh"],
    "this":    ["dis", "diss", "tis"],
    "that":    ["dat", "dhat", "tat"],
    "there":   ["dare", "der", "dere", "dair"],
    "then":    ["den", "ten"],
    "thank":   ["dank", "tank", "fank"],
    "think":   ["dink", "tink", "fink"],
    "through": ["frough", "drough", "troo"],
    "rabbit":  ["wabbit", "labbit", "habbit"],
    "red":     ["wed", "led", "wred"],
    "rain":    ["wain", "lain"],
    "rainbow": ["wainbow", "lainbow"],
    "run":     ["wun", "lun"],
    "rocket":  ["wocket", "locket"],
    "river":   ["wiver", "liver"],
    "ring":    ["wing", "ling"],
    "rock":    ["wock", "lock"],
    "road":    ["woad", "load"],
    "right":   ["wight", "light"],
}


SYLLABLES = {
    # Animals
    "elephant":    "el · e · phant",
    "butterfly":   "but · ter · fly",
    "rabbit":      "rab · bit",
    "turtle":      "tur · tle",
    "penguin":     "pen · guin",
    "monkey":      "mon · key",
    "tiger":       "ti · ger",
    "lion":        "li · on",
    "camel":       "cam · el",
    # Fruits
    "banana":      "ba · na · na",
    "strawberry":  "straw · ber · ry",
    "watermelon":  "wa · ter · mel · on",
    "orange":      "or · ange",
    "cherry":      "cher · ry",
    "mango":       "man · go",
    "lemon":       "lem · on",
    "apple":       "ap · ple",
    "grape":       "grape",
    # Kitchen
    "spoon":       "spoon",
    "butter":      "but · ter",
    "fridge":      "fridge",
    # Bedroom
    "pillow":      "pil · low",
    "blanket":     "blan · ket",
    "mirror":      "mir · ror",
    "window":      "win · dow",
    # Clothes
    "jacket":      "jack · et",
    "gloves":      "gloves",
    "sandals":     "san · dals",
    "pajamas":     "pa · ja · mas",
    # Body
    "finger":      "fin · ger",
    "elbow":       "el · bow",
    "shoulder":    "shoul · der",
    "stomach":     "stom · ach",
    # Vehicles
    "helicopter":  "hel · i · cop · ter",
    "bicycle":     "bi · cy · cle",
    "tractor":     "trac · tor",
    "rocket":      "rock · et",
    # Weather
    "rainbow":     "rain · bow",
    "thunder":     "thun · der",
    "stormy":      "storm · y",
    # Easy Phrases
    "morning":     "morn · ing",
    "hungry":      "hun · gry",
    "happy":       "hap · py",
    "tired":       "tired",
    # Colors
    "purple":      "pur · ple",
    "yellow":      "yel · low",
    "orange":      "or · ange",
    # Numbers
    "seven":       "sev · en",
    "eight":       "eight",
    "nine":        "nine",
}


def is_correct(recognized, target):
    recognized = recognized.lower().strip()
    target = target.lower().strip()

    # Exact / substring match
    if target in recognized or recognized in target:
        return True

    rec_words = recognized.split()
    target_words = target.split()

    # Sound aliases — accept Hebrew-speaker mispronunciations
    for t_word in target_words:
        for alias in SOUND_ALIASES.get(t_word, []):
            if alias in recognized or recognized in alias:
                return True
            if any(SequenceMatcher(None, alias, rw).ratio() >= 0.75 for rw in rec_words):
                return True

    # Sentences: accept if ~25% of key words are recognisable
    if len(target_words) > 1:
        key = [w for w in target_words if len(w) > 3] or target_words
        hits = sum(
            1 for kw in key
            if any(SequenceMatcher(None, kw, rw).ratio() >= 0.45 for rw in rec_words)
        )
        return hits / len(key) >= 0.25

    # Single word — toddler-friendly matching
    for rw in rec_words:
        # Same first two letters → accept (captures "tat"→"cat", "doh"→"dog", etc.)
        if len(rw) >= 2 and len(target) >= 2 and rw[:2] == target[:2]:
            return True
        # Same first letter AND similar length (within 2 chars)
        if rw and target and rw[0] == target[0] and abs(len(rw) - len(target)) <= 2:
            return True
        # Fuzzy similarity at a very gentle threshold
        if SequenceMatcher(None, rw, target).ratio() >= 0.36:
            return True

    return False


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def init_state():
    if "progress" not in st.session_state:
        p = load_progress()
        p = update_streak(p)
        st.session_state.progress       = p
        st.session_state.child_name     = p.get("child_name")
        st.session_state.progress_dirty = True

    defaults = {
        "mode":           "practice",
        "category":       "🐾 Animals",
        "word_list":      [],
        "idx":            0,
        "score":          0,
        "attempts":       0,
        "feedback":       None,
        "story_key":      None,
        "story_idx":      0,
        "story_done":     False,
        "choice_options": [],
        "choice_answered":False,
        "choice_correct": False,
        "wrong_words":    [],
        "sr_counter":     0,
        "show_parent":    False,
        "music_playing":  False,
        "play_count":     0,
        "new_badges":     [],
        "progress_dirty": False,
        "current_word":        None,   # locked-in word for current practice turn
        "story_sound_played":  False,  # prevents badge sound replaying on every render
        "level_up_pending":    None,
        "milestone_pending":   None,   # score milestone (5, 10, 15...) waiting to be shown
        "current_word_tries":  0,      # wrong attempts on current word; resets on new word
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def load_category(cat):
    wl = get_all_categories().get(cat, []).copy()
    random.shuffle(wl)
    st.session_state.category    = cat
    st.session_state.word_list   = wl
    st.session_state.idx         = 0
    st.session_state.feedback    = None
    st.session_state.wrong_words = []
    st.session_state.sr_counter  = 0
    st.session_state.current_word = None


def pick_next_word():
    sr = st.session_state.sr_counter
    st.session_state.sr_counter += 1
    ww = st.session_state.wrong_words
    if sr % 3 == 0 and ww:
        return ww.pop(0)
    wl = st.session_state.word_list
    if not wl:
        return {"text": "cat", "emoji": "🐱"}
    w = wl[st.session_state.idx % len(wl)]
    st.session_state.idx += 1
    if st.session_state.idx >= len(wl):
        random.shuffle(wl)
        st.session_state.idx = 0
    st.session_state.current_word_tries = 0
    return w


def build_choice_options(correct):
    """Returns (shuffled_options, correct_text). Store correct_text separately — it's lost after shuffle."""
    all_w = [w for wl in get_all_categories().values() for w in wl]
    others = [w for w in all_w if w["text"] != correct["text"]]
    wrong = random.sample(others, min(2, len(others)))
    opts = [correct] + wrong
    random.shuffle(opts)
    return opts, correct["text"]


init_state()

if not st.session_state.word_list:
    load_category(st.session_state.category)


# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #FBF7F0 !important;
    font-family: 'Nunito', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Floating background ── */
@keyframes leaf-float {
    0%   { transform: translateY(110vh) rotate(0deg);   opacity: 0; }
    5%   { opacity: 0.35; }
    95%  { opacity: 0.25; }
    100% { transform: translateY(-120px) rotate(720deg); opacity: 0; }
}
.bg-leaf {
    position: fixed; pointer-events: none; z-index: 0;
    animation: leaf-float linear infinite;
    user-select: none;
}

/* ── Word card ── */
.word-card {
    background: #FFFFFF; border-radius: 28px; padding: 28px 20px 20px;
    box-shadow: 0 6px 30px rgba(100,70,40,0.10); text-align: center;
    margin: 4px auto; border: 2px solid #F0E8D8; position: relative; z-index: 1;
}
.word-emoji  { font-size: 120px; line-height: 1.15; }
.word-text   { font-size: 48px; font-weight: 800; color: #3D2B1F;
               letter-spacing: 3px; margin-top: 6px; }

/* ── Story card ── */
.story-card {
    background: linear-gradient(160deg, #FFFDF8 0%, #FFF4E6 100%);
    border-radius: 28px; padding: 24px 20px;
    box-shadow: 0 6px 30px rgba(100,70,40,0.12); border: 2px solid #F0E8D8;
    margin-bottom: 10px; position: relative; z-index: 1;
}
@keyframes scene-float {
    0%, 100% { transform: translateY(0px) scale(1); }
    50%       { transform: translateY(-14px) scale(1.06); }
}
@keyframes emoji-bounce {
    0%   { transform: scale(0.4) rotate(-12deg); opacity: 0; }
    55%  { transform: scale(1.25) rotate(4deg); opacity: 1; }
    80%  { transform: scale(0.92) rotate(-2deg); }
    100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
.story-scene {
    font-size: 56px; text-align: center; letter-spacing: 12px;
    display: block; margin-bottom: 4px;
}
.story-emoji-pop {
    font-size: 100px; text-align: center; display: block;
    animation: emoji-bounce 0.7s cubic-bezier(0.175,0.885,0.32,1.275) both;
}
.story-text { font-size: 19px; color: #5A4030; line-height: 1.8;
              text-align: center; white-space: pre-line; margin: 10px 0; }
.story-word { font-size: 46px; font-weight: 800; color: #C17A4A;
              text-align: center; letter-spacing: 4px; }

/* ── Progress dots ── */
.progress-row { text-align: center; font-size: 24px; letter-spacing: 6px; margin: 6px 0 14px; }

/* ── Star row (replaces score-bar) ── */
.star-row { text-align: center; font-size: 28px; margin: 4px 0 8px;
            letter-spacing: 4px; position: relative; z-index: 1; }
.star-level { font-size: 14px; color: #9A7A5A; font-weight: 700;
              text-align: center; margin-bottom: 6px; }

/* ── WOTD ── */
.wotd-card {
    background: #FFF8EE; border-radius: 16px; padding: 10px 16px;
    border: 2px solid #F5DEB3; text-align: center; margin: 6px 0;
    position: relative; z-index: 1;
}
.wotd-label { font-size: 13px; color: #9A7A5A; font-weight: 600; }
.wotd-word  { font-size: 28px; font-weight: 800; color: #C17A4A; }

/* ── Badge shelf ── */
.badge-shelf {
    display: flex; overflow-x: auto; gap: 8px; padding: 6px 2px;
    scrollbar-width: none; margin-bottom: 4px; position: relative; z-index: 1;
}
.badge-shelf::-webkit-scrollbar { display: none; }
.badge-item {
    background: #FFF8EE; border-radius: 14px; padding: 6px 10px;
    border: 2px solid #F5DEB3; white-space: nowrap; flex-shrink: 0;
    font-size: 14px; font-weight: 700; color: #7A5C3A;
}
.badge-locked { background: #F5F5F5; border-color: #E0E0E0; color: #BDBDBD; }
.badge-new-announce {
    background: #FFF9C4; border-radius: 20px; padding: 12px 20px;
    font-size: 26px; font-weight: 800; color: #856404;
    text-align: center; margin: 8px auto;
    animation: badge-pop 0.6s ease-out;
}

/* ── Feedback ── */
.fb-yes { font-size: 38px; font-weight: 800; color: #4A7C59; text-align: center; padding: 10px; }
.fb-no  { font-size: 26px; color: #A0522D; text-align: center; line-height: 1.6; padding: 8px; }

/* ── Category buttons ── */
.cat-btn .stButton > button {
    background: #FFF8EE !important;
    border: 2px solid #F5DEB3 !important;
    border-radius: 16px !important;
    font-size: 14px !important;
    padding: 8px 4px !important;
    color: #7A5C3A !important;
    min-height: 52px !important;
    font-weight: 700 !important;
}
.cat-btn-active .stButton > button {
    background: #C17A4A !important;
    border: 2px solid #A06030 !important;
    color: white !important;
    font-weight: 800 !important;
}

/* ── Choice buttons (single tappable card) ── */
.choice-btn .stButton > button {
    min-height: 150px !important;
    font-size: 46px !important;
    background: #FFFFFF !important;
    border: 3px solid #F0E8D8 !important;
    border-radius: 22px !important;
    box-shadow: 0 4px 20px rgba(100,70,40,0.08) !important;
    color: #3D2B1F !important;
    padding: 14px 6px !important;
    line-height: 1.25 !important;
    font-weight: 800 !important;
    transition: transform 0.1s, box-shadow 0.1s !important;
}
.choice-btn .stButton > button:hover {
    border-color: #C17A4A !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 28px rgba(100,70,40,0.18) !important;
}
.choice-correct .stButton > button {
    border-color: #4A7C59 !important; background: #E8F5E9 !important;
}
.choice-wrong .stButton > button {
    border-color: #C62828 !important; background: #FFEBEE !important;
}

/* ── Story select ── */
.story-select-card {
    background: #FFFFFF; border-radius: 22px; padding: 20px 10px;
    box-shadow: 0 4px 16px rgba(100,70,40,0.08); text-align: center;
    border: 2px solid #F0E8D8; cursor: pointer;
}
.story-select-card:hover { border-color: #C17A4A; }

/* ── Level-up banner ── */
.levelup-banner {
    background: linear-gradient(135deg, #FFD700 0%, #FF8C00 100%);
    border-radius: 24px; padding: 28px 20px; text-align: center;
    box-shadow: 0 8px 32px rgba(255,140,0,0.35); margin: 10px 0;
    animation: badge-pop 0.6s ease-out;
    position: relative; z-index: 1;
}

/* ── Milestone banner ── */
.milestone-banner {
    background: linear-gradient(135deg, #FF6B9D 0%, #C44FD8 50%, #7B68EE 100%);
    border-radius: 28px; padding: 36px 20px; text-align: center;
    box-shadow: 0 10px 40px rgba(196,79,216,0.45); margin: 10px 0;
    animation: badge-pop 0.5s cubic-bezier(0.175,0.885,0.32,1.275);
    position: relative; z-index: 1;
}

/* ── Mic pulsing ring ── */
@keyframes mic-pulse {
    0%, 100% { box-shadow: 0 0 0 0   rgba(193,122,74,0.55),
                            0 0 0 0   rgba(193,122,74,0.30); }
    50%       { box-shadow: 0 0 0 14px rgba(193,122,74,0.15),
                            0 0 0 28px rgba(193,122,74,0.05); }
}
.mic-ring {
    display: flex; justify-content: center; align-items: center;
    border-radius: 50%; animation: mic-pulse 1.6s ease-in-out infinite;
    width: fit-content; margin: 0 auto;
}

/* ── Animations ── */
@keyframes badge-pop {
    0%   { transform: scale(0.5); opacity: 0; }
    60%  { transform: scale(1.1); }
    100% { transform: scale(1);   opacity: 1; }
}
@keyframes celebrate {
    0%   { transform: scale(0.5) rotate(-10deg); opacity: 0; }
    50%  { transform: scale(1.2) rotate(5deg); }
    100% { transform: scale(1)   rotate(0deg); opacity: 1; }
}
.celebrate-emoji {
    display: block; text-align: center; font-size: 80px;
    animation: celebrate 0.5s ease-out;
}

/* ── Buttons (global) ── */
.stButton > button {
    border-radius: 16px !important; font-size: 18px !important;
    font-weight: 700 !important; padding: 10px 18px !important;
    position: relative; z-index: 1;
}

/* ── Parent dashboard ── */
.parent-section {
    background: #F0EDE6; border-radius: 20px; padding: 20px;
    border: 2px solid #D5C8B0; margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)


# Floating background leaves / flowers
st.markdown("""
<div aria-hidden="true">
  <span class="bg-leaf" style="left:5%;font-size:28px;animation-duration:18s;animation-delay:0s;">🍃</span>
  <span class="bg-leaf" style="left:18%;font-size:22px;animation-duration:22s;animation-delay:3s;">🌸</span>
  <span class="bg-leaf" style="left:33%;font-size:26px;animation-duration:16s;animation-delay:7s;">🍀</span>
  <span class="bg-leaf" style="left:50%;font-size:20px;animation-duration:25s;animation-delay:1s;">⭐</span>
  <span class="bg-leaf" style="left:65%;font-size:24px;animation-duration:20s;animation-delay:5s;">🌺</span>
  <span class="bg-leaf" style="left:80%;font-size:18px;animation-duration:17s;animation-delay:9s;">🍃</span>
  <span class="bg-leaf" style="left:90%;font-size:22px;animation-duration:23s;animation-delay:2s;">🌼</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# NAME ENTRY GATE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.child_name:
    st.markdown("""
    <div class='word-card' style='max-width:420px;margin:60px auto;padding:40px 30px;'>
        <div style='font-size:80px;'>🌿</div>
        <div style='font-size:32px;font-weight:800;color:#3D2B1F;margin:12px 0 6px;'>
            Welcome to English Garden!
        </div>
        <div style='font-size:18px;color:#7A5C3A;margin-bottom:20px;'>
            What is your name?
        </div>
    </div>
    """, unsafe_allow_html=True)
    name_input = st.text_input("", placeholder="Type your name here...", label_visibility="collapsed")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🌸  Let's go!", use_container_width=True) and name_input.strip():
            st.session_state.child_name = name_input.strip()
            st.session_state.progress["child_name"] = name_input.strip()
            st.session_state.progress_dirty = True
            flush_progress()
            st.rerun()
    flush_progress()   # save streak update even if user hasn't entered name yet
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
name    = st.session_state.child_name
streak  = st.session_state.progress.get("streak_days", 0)
wotd    = get_word_of_the_day()

h1, h2, h3 = st.columns([1, 2, 1])
with h1:
    st.markdown(
        f"<div style='font-size:22px;font-weight:800;color:#C17A4A;padding-top:8px;'>"
        f"🔥 {streak} day{'s' if streak != 1 else ''}</div>",
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        f"<h1 style='text-align:center;color:#7A5C3A;font-size:36px;"
        f"font-family:Nunito,sans-serif;font-weight:800;margin:0;'>🌿 English Garden 🌿</h1>"
        f"<div style='text-align:center;font-size:18px;color:#C17A4A;font-weight:700;'>Hi {name}! 🌸</div>",
        unsafe_allow_html=True,
    )
with h3:
    btn_cols = st.columns(2)
    with btn_cols[0]:
        music_icon = "🔇" if st.session_state.music_playing else "🎵"
        if st.button(music_icon, use_container_width=True, key="music_toggle"):
            st.session_state.music_playing = not st.session_state.music_playing
            inject_ambient_music(st.session_state.music_playing)
            st.rerun()
    with btn_cols[1]:
        if st.button("👨‍👩‍👧", use_container_width=True, key="parent_toggle"):
            st.session_state.show_parent = not st.session_state.show_parent
            st.rerun()

# Word of the Day
st.markdown(
    f"<div class='wotd-card'>"
    f"<span class='wotd-label'>⭐ Word of the Day</span><br>"
    f"<span style='font-size:40px;'>{wotd['emoji']}</span> "
    f"<span class='wotd-word'>{wotd['text'].capitalize()}</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# Badge shelf
earned = st.session_state.progress.get("badges_earned", [])
shelf_html = "<div class='badge-shelf'>"
for b in BADGES:
    cls  = "badge-item" if b["key"] in earned else "badge-item badge-locked"
    lbl  = b["label"] if b["key"] in earned else "🔒 " + b["desc"]
    shelf_html += f"<div class='{cls}' title='{b['desc']}'>{lbl}</div>"
shelf_html += "</div>"
st.markdown(shelf_html, unsafe_allow_html=True)

# New badge announcements
if st.session_state.new_badges:
    for b in st.session_state.new_badges:
        st.markdown(f"<div class='badge-new-announce'>🎉 New Badge: {b['label']}!</div>", unsafe_allow_html=True)
        play_sound("badge")
    st.session_state.new_badges = []

# Star row
sc = st.session_state.score
level_names = {1: "Starter 🌱", 2: "Explorer 🌿", 3: "Champion 🌳", 4: "Star ⭐"}
lvl = level_names.get(st.session_state.progress.get("difficulty_level", 1), "Starter 🌱")
stars_filled = min(sc, 10)
star_display = "⭐" * stars_filled + "☆" * (10 - stars_filled) if sc <= 10 else "⭐" * 10 + f" +{sc - 10}"
st.markdown(f"<div class='star-level'>{lvl}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='star-row'>{star_display}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PARENT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_parent:
    p = st.session_state.progress
    st.markdown("---")
    st.markdown("### 👨‍👩‍👧 Parent Dashboard")

    # Stats
    st.markdown(
        f"**Total correct:** {p.get('total_correct',0)}  |  "
        f"**Streak:** {p.get('streak_days',0)} days  |  "
        f"**Stories done:** {len(p.get('stories_completed',[]))}"
    )

    # Category accuracy
    cs = p.get("category_stats", {})
    if cs:
        st.markdown("**Category accuracy:**")
        rows = []
        for cat, stats in cs.items():
            c, w = stats.get("correct", 0), stats.get("wrong", 0)
            tot = c + w
            acc = f"{int(c/tot*100)}%" if tot else "—"
            rows.append(f"| {cat} | {c} ✅ | {w} ❌ | {acc} |")
        st.markdown("| Category | Correct | Wrong | Accuracy |\n|---|---|---|---|\n" + "\n".join(rows))

    # Struggling words
    ws = p.get("word_stats", {})
    if ws:
        hard = sorted(ws.items(), key=lambda x: x[1].get("wrong", 0), reverse=True)[:10]
        if hard[0][1].get("wrong", 0) > 0:
            st.markdown("**Words to practise more:**")
            st.markdown(", ".join(f"**{w}** ({s['wrong']}❌)" for w, s in hard if s.get("wrong", 0) > 0))

    st.markdown("---")
    # Custom word adder
    st.markdown("**Add a custom word:**")
    EMOJI_OPTIONS = ["🌟","👧","👦","🐶","🐱","🏠","🚗","⚽","🎈","🍕","🌈","❤️","🦁","🐘","🌸","🍦","📚","✏️","🎸","🚀"]
    cc1, cc2, cc3 = st.columns([3, 2, 1])
    with cc1:
        new_word = st.text_input("Word", placeholder="e.g. grandma", label_visibility="collapsed", key="cw_input")
    with cc2:
        new_emoji = st.selectbox("Emoji", EMOJI_OPTIONS, label_visibility="collapsed", key="cw_emoji")
    with cc3:
        if st.button("Add ➕", use_container_width=True) and new_word.strip():
            entry = {"text": new_word.strip().lower(), "emoji": new_emoji}
            if entry not in p.get("custom_words", []):
                p.setdefault("custom_words", []).append(entry)
                st.session_state.progress_dirty = True
                new_bgs = check_badges(p)
                if new_bgs:
                    st.session_state.new_badges += new_bgs
                st.rerun()

    st.markdown("---")
    # Progress backup
    st.markdown("**Progress backup:**")
    pb1, pb2 = st.columns(2)
    with pb1:
        st.download_button(
            "💾 Download progress",
            data=json.dumps(p, indent=2, ensure_ascii=False),
            file_name="english_garden_progress.json",
            mime="application/json",
            use_container_width=True,
        )
    with pb2:
        uploaded = st.file_uploader("📂 Load progress", type="json", label_visibility="collapsed", key="prog_upload")
        if uploaded:
            loaded = json.loads(uploaded.read())
            st.session_state.progress   = loaded
            st.session_state.child_name = loaded.get("child_name")
            st.session_state.progress_dirty = True
            st.rerun()

    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# LEVEL-UP CEREMONY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("level_up_pending"):
    new_lvl = st.session_state.level_up_pending
    level_names_map = {2: ("Explorer 🌿", "🌿"), 3: ("Champion 🌳", "🏆"), 4: ("Star ⭐", "⭐")}
    lvl_name, lvl_icon = level_names_map.get(new_lvl, ("Star ⭐", "⭐"))
    st.markdown(f"""
    <div class='levelup-banner'>
        <div style='font-size:80px;'>{lvl_icon}</div>
        <div style='font-size:32px;font-weight:900;color:#3D2B1F;margin:8px 0 4px;'>Level Up!</div>
        <div style='font-size:20px;font-weight:700;color:#5D3B1F;'>You are now a <b>{lvl_name}</b>!</div>
    </div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🎉  Woohoo!", use_container_width=True, key="levelup_dismiss"):
            del st.session_state["level_up_pending"]
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MILESTONE PARTY SCREEN (every 5 correct answers)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("milestone_pending"):
    ms = st.session_state.milestone_pending
    icons = ["🌟", "🎉", "🦋", "🏆", "🌈", "🎊", "⭐", "🌸"]
    icon = icons[(ms // 5 - 1) % len(icons)]
    st.markdown(f"""
    <div class='milestone-banner'>
        <div style='font-size:100px;line-height:1;'>{icon}</div>
        <div style='font-size:38px;font-weight:900;color:white;margin:10px 0 4px;
                    text-shadow:0 2px 8px rgba(0,0,0,0.25);'>
            {ms} Stars! 🎉
        </div>
        <div style='font-size:22px;font-weight:700;color:rgba(255,255,255,0.92);'>
            You are absolutely AMAZING!
        </div>
    </div>""", unsafe_allow_html=True)
    play_sound("badge")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🎉  Keep going!", use_container_width=True, key="milestone_dismiss"):
            st.session_state.milestone_pending = None
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MODE SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🔤  Practice", use_container_width=True):
        st.session_state.mode = "practice"; st.session_state.feedback = None; st.rerun()
with m2:
    if st.button("🎯  Choose", use_container_width=True):
        st.session_state.mode = "choice"; st.session_state.feedback = None
        st.session_state.choice_answered = False; st.rerun()
with m3:
    if st.button("📖  Stories", use_container_width=True):
        st.session_state.mode = "story"; st.session_state.story_key = None
        st.session_state.feedback = None; st.rerun()

st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: handle a correct / wrong answer (shared by practice & choice)
# ══════════════════════════════════════════════════════════════════════════════
def handle_answer(word_dict, category, correct, heard):
    record_answer(word_dict["text"], category, correct)
    new_bgs = check_badges(st.session_state.progress)
    if new_bgs:
        st.session_state.new_badges += new_bgs
    # Difficulty unlock
    old_lvl = st.session_state.progress.get("difficulty_level", 1)
    tc = st.session_state.progress.get("total_correct", 0)
    cur_lvl = st.session_state.progress.get("difficulty_level", 1)
    thresholds = {1: 10, 2: 25, 3: 50}
    if cur_lvl in thresholds and tc >= thresholds[cur_lvl]:
        st.session_state.progress["difficulty_level"] = cur_lvl + 1
        st.session_state.progress_dirty = True
    new_lvl = st.session_state.progress.get("difficulty_level", 1)
    if new_lvl > old_lvl:
        st.session_state.level_up_pending = new_lvl
    if correct:
        st.session_state.score += 1
        st.session_state.feedback = ("correct", heard)
        play_sound("correct")
        st.balloons()
        show_splash("🌟", "Amazing!")
        # Milestone every 5 correct answers
        if st.session_state.score % 5 == 0:
            st.session_state.milestone_pending = st.session_state.score
    else:
        st.session_state.feedback = ("wrong", heard)
        play_sound("wrong")
        st.session_state.current_word_tries += 1
        ww = st.session_state.wrong_words
        if word_dict not in ww:
            ww.append(word_dict)
    st.session_state.attempts += 1


# ══════════════════════════════════════════════════════════════════════════════
# STORY MODE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == "story":

    # Story selection
    if st.session_state.story_key is None:
        st.markdown(
            "<h3 style='text-align:center;color:#7A5C3A;'>Choose a story! 📖</h3>",
            unsafe_allow_html=True,
        )
        completed = st.session_state.progress.get("stories_completed", [])
        cols = st.columns(3)
        for i, (key, (steps, label)) in enumerate(ALL_STORIES.items()):
            with cols[i % 3]:
                done_mark = " ✅" if key in completed else ""
                if st.button(f"{label}{done_mark}", use_container_width=True, key=f"story_pick_{key}"):
                    st.session_state.story_key  = key
                    st.session_state.story_idx  = 0
                    st.session_state.story_done = False
                    st.session_state.feedback   = None
                    st.rerun()

    # Story done screen
    elif st.session_state.story_done:
        _, (steps, label) = list(ALL_STORIES.items())[0]   # fallback
        for k, (s, l) in ALL_STORIES.items():
            if k == st.session_state.story_key:
                steps, label = s, l
        final_emoji = steps[-1]["emoji"]
        st.markdown(f"""
        <div style='text-align:center;padding:30px 0;'>
            <div class='celebrate-emoji'>{final_emoji}</div>
            <div style='font-size:32px;font-weight:800;color:#C17A4A;margin:12px 0;'>The End! 🎉</div>
            <div style='font-size:20px;color:#5A4030;'>You told the whole {label} story!</div>
        </div>""", unsafe_allow_html=True)
        # Play fanfare only once when story first completes
        if not st.session_state.get("story_sound_played"):
            play_sound("badge")
            st.session_state.story_sound_played = True
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🔄  Read again!", use_container_width=True):
                st.session_state.story_idx          = 0
                st.session_state.story_done         = False
                st.session_state.story_sound_played = False
                st.session_state.feedback           = None
                st.rerun()
            if st.button("📖  Pick another story", use_container_width=True):
                st.session_state.story_key = None
                st.session_state.feedback  = None
                st.rerun()

    # Story step
    else:
        if st.session_state.story_key not in ALL_STORIES:
            st.session_state.story_key = None
            st.rerun()
        story_steps, story_label = ALL_STORIES[st.session_state.story_key]
        total = len(story_steps)
        idx   = st.session_state.story_idx
        step  = story_steps[idx]

        dots = "".join("🟤" if i < idx else ("🟠" if i == idx else "⚪") for i in range(total))
        st.markdown(f"<div class='progress-row'>{dots}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='text-align:center;color:#9A7A5A;font-size:15px;margin-bottom:6px;'>"
            f"Step {idx+1} of {total} — {story_label}</div>", unsafe_allow_html=True,
        )

        txt_display = step['text'].capitalize()
        story_autoplay_key = f"story_autoplayed_{st.session_state.story_key}_{idx}"
        if not st.session_state.get(story_autoplay_key):
            # Speak narration then the target word
            speak_story_step(step["narration"], step["text"])
            st.session_state[story_autoplay_key] = True

        # Per-story card background
        story_bg, story_accent = STORY_COLORS.get(
            st.session_state.story_key,
            ("linear-gradient(160deg, #FFFDF8 0%, #FFF4E6 100%)", "#C17A4A"),
        )
        scene_html = animated_scene(step["scene"])

        st.markdown(f"""
        <div class='story-card' style='background:{story_bg};'>
            <div class='story-scene'>{scene_html}</div>
            <div class='story-text'>{step['narration']}</div>
            <hr style='border:1px solid #F0E8D8;margin:10px 0;'>
            <div style='font-size:15px;color:#9A7A5A;text-align:center;font-weight:600;'>🎤 Can you say this word?</div>
            <div class='story-emoji-pop'>{step['emoji']}</div>
            <div class='story-word' style='color:{story_accent};'>{txt_display}</div>
        </div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🔊  Hear it!", use_container_width=True, key="story_hear"):
                speak_instant(step["text"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;font-size:17px;color:#9A7A5A;font-weight:700;margin-bottom:4px;'>"
            "👇 Tap the mic, then say the word!</div>",
            unsafe_allow_html=True,
        )
        inject_mic_listener()
        st.markdown("<div class='mic-ring'>", unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="", recording_color="#C17A4A", neutral_color="#BBA890",
            icon_size="3x", pause_threshold=0.7,
            key=f"story_{st.session_state.story_key}_{idx}_{st.session_state.attempts}",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if audio_bytes:
            playback_child_voice(audio_bytes)
            recognized, err = try_recognize(audio_bytes)
            if recognized:
                handle_answer(step, "📖 Stories", is_correct(recognized, step["text"]), recognized)
            elif err == "quiet":
                st.markdown("<div class='fb-no'>🙈 I didn't hear anything!<br>Speak a little louder! 🌈</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='fb-no'>Oops! Let's try again! 🌈</div>", unsafe_allow_html=True)

        if st.session_state.feedback:
            kind, heard = st.session_state.feedback
            if kind == "correct":
                st.markdown(f"<div class='celebrate-emoji'>{step['emoji']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='fb-yes'>✨ {step['praise']} ✨</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2:
                    lbl = "🎉  Finish!" if step.get("final") else "➡️  Next!"
                    if st.button(lbl, use_container_width=True, key="story_next"):
                        st.session_state.feedback = None
                        if step.get("final"):
                            st.session_state.story_done = True
                            sk = st.session_state.story_key
                            completed = st.session_state.progress.setdefault("stories_completed", [])
                            if sk not in completed:
                                completed.append(sk)
                                st.session_state.progress_dirty = True
                                new_bgs = check_badges(st.session_state.progress)
                                if new_bgs:
                                    st.session_state.new_badges += new_bgs
                        else:
                            st.session_state.story_idx += 1
                        st.rerun()
            else:
                # Auto-replay the target word and show encouragement
                speak_instant(step["text"])
                encouragements = [
                    "Almost! You can do it! 💪",
                    "So close! Try one more time! 🌟",
                    "Keep going, superstar! ⭐",
                    "Nearly there! Give it another go! 🌈",
                ]
                enc = encouragements[st.session_state.attempts % len(encouragements)]
                st.markdown(
                    f"<div class='fb-no'>{enc}<br>"
                    f"<span style='font-size:42px;font-weight:900;color:{story_accent};'>"
                    f"{step['emoji']} {txt_display}</span></div>",
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# CHOICE MODE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "choice":

    # Pick a word if we don't have options yet
    if not st.session_state.choice_options:
        current = pick_next_word()
        opts, correct_text = build_choice_options(current)   # correct_text saved BEFORE shuffle
        st.session_state.choice_options      = opts
        st.session_state.choice_correct_word = correct_text
        st.session_state.choice_answered     = False
        st.session_state.choice_correct      = False
        speak_instant(correct_text)

    opts         = st.session_state.choice_options
    correct_text = st.session_state.choice_correct_word

    st.markdown(
        f"<div style='text-align:center;font-size:22px;font-weight:800;color:#7A5C3A;margin:8px 0;'>"
        f"👂 Which one did you hear?</div>",
        unsafe_allow_html=True,
    )
    ct_len = len(correct_text)
    ct_size = "24px" if ct_len > 20 else "34px" if ct_len > 10 else "44px"
    ct_spacing = "0px" if ct_len > 10 else "3px"
    st.markdown(
        f"<div style='text-align:center;font-size:{ct_size};font-weight:800;color:#C17A4A;"
        f"letter-spacing:{ct_spacing};margin-bottom:10px;'>{correct_text.capitalize()}</div>",
        unsafe_allow_html=True,
    )

    # Replay button
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔊  Hear it again!", use_container_width=True, key="choice_hear"):
            speak_instant(correct_text)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3 choice buttons — single tappable card per option
    answered = st.session_state.choice_answered
    cols = st.columns(3)
    for i, opt in enumerate(opts):
        with cols[i]:
            if answered:
                # After answer: show decorative card with result colour
                border_cls = "choice-correct" if opt["text"] == correct_text else "choice-wrong"
                st.markdown(
                    f"<div class='choice-card {border_cls}'>"
                    f"<div class='choice-emoji'>{opt['emoji']}</div>"
                    f"<div style='font-size:20px;font-weight:800;color:#3D2B1F;'>{opt['text'].capitalize()}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            else:
                # Before answer: big tappable button (emoji + word, no separate card)
                st.markdown("<div class='choice-btn'>", unsafe_allow_html=True)
                if st.button(
                    f"{opt['emoji']}  {opt['text'].capitalize()}",
                    use_container_width=True,
                    key=f"choice_btn_{i}",
                ):
                    correct_ans = opt["text"] == correct_text
                    handle_answer(
                        next(o for o in opts if o["text"] == correct_text),
                        st.session_state.category,
                        correct_ans,
                        opt["text"],
                    )
                    st.session_state.choice_answered = True
                    st.session_state.choice_correct  = correct_ans
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    if answered:
        if st.session_state.choice_correct:
            st.markdown("<div class='fb-yes'>🎉 YES! That's right! 🎉</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='fb-no'>The right answer was <b style='color:#C17A4A'>{correct_text.capitalize()}</b>!</div>",
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("➡️  Next word!", use_container_width=True, key="choice_next"):
                del st.session_state["choice_correct_word"]
                st.session_state.choice_options  = []
                st.session_state.choice_answered = False
                st.session_state.feedback        = None
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PRACTICE MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    # Category selector — styled cards, 4 per row
    all_cats = list(get_all_categories().keys())
    for row_start in range(0, len(all_cats), 4):
        row = all_cats[row_start:row_start + 4]
        rcols = st.columns(len(row))
        for col, cat in zip(rcols, row):
            with col:
                active = cat == st.session_state.category
                wrapper = "cat-btn-active" if active else "cat-btn"
                st.markdown(f"<div class='{wrapper}'>", unsafe_allow_html=True)
                if st.button(cat, use_container_width=True, key=f"cat_{cat}"):
                    load_category(cat)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sentence Build-Up Mode (only for 📝 Sentences category) ──────────────
    if st.session_state.category == "📝 Sentences":
        if st.session_state.current_word is None:
            st.session_state.current_word = pick_next_word()
            words = st.session_state.current_word["text"].split()
            # Build checkpoint steps: [1 word], [1+2 words], ..., [all words]
            if len(words) <= 3:
                steps = [words]
            elif len(words) <= 5:
                steps = [words[:2], words[:len(words)//2], words]
            else:
                steps = []
                for i in range(2, len(words) + 1, 2):
                    steps.append(words[:i])
                if steps[-1] != words:
                    steps.append(words)
            st.session_state["buildup_steps"] = steps
            st.session_state["buildup_step"] = 0
            st.session_state.pop("buildup_autoplayed", None)

        current   = st.session_state.current_word
        steps     = st.session_state.get("buildup_steps", [current["text"].split()])
        step_idx  = st.session_state.get("buildup_step", 0)
        step_idx  = min(step_idx, len(steps) - 1)
        partial   = " ".join(steps[step_idx])
        all_words = current["text"].split()
        total_steps = len(steps)
        is_final    = step_idx == total_steps - 1

        # Step progress bar
        prog_html = "".join(
            f"<span style='font-size:18px;'>{'🟠' if i == step_idx else ('✅' if i < step_idx else '⚪')}</span>"
            for i in range(total_steps)
        )
        st.markdown(
            f"<div style='text-align:center;margin-bottom:8px;'>{prog_html}"
            f"<span style='font-size:14px;color:#9A7A5A;margin-left:8px;'>Step {step_idx+1} of {total_steps}</span></div>",
            unsafe_allow_html=True,
        )

        # Show sentence with current words highlighted and future words greyed
        highlighted = ""
        for i, w in enumerate(all_words):
            if i < len(steps[step_idx]):
                highlighted += f"<b style='color:#3D2B1F;'>{w.capitalize() if i==0 else w}</b> "
            else:
                highlighted += f"<span style='color:#D0C0B0;'>{w}</span> "
        st.markdown(
            f"<div class='word-card'>"
            f"<div style='font-size:48px;margin-bottom:8px;'>{current['emoji']}</div>"
            f"<div style='font-size:{'28px' if len(partial)>20 else '36px'};line-height:1.4;padding:0 10px;'>{highlighted.strip()}</div>"
            f"<div style='font-size:16px;color:#9A7A5A;margin-top:8px;'>Say the {'bold' if not is_final else 'whole sentence'} part!</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Auto-speak partial on each step
        auto_key = f"buildup_{current['text']}_{step_idx}"
        if st.session_state.get("buildup_autoplayed") != auto_key:
            speak_then_record(partial)
            st.session_state.buildup_autoplayed = auto_key

        st.markdown("<br>", unsafe_allow_html=True)
        c1h, c2h, c3h = st.columns([1, 2, 1])
        with c2h:
            if st.button("🔊  Hear it!", use_container_width=True, key="buildup_hear"):
                speak_instant(partial)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<div style='text-align:center;font-size:17px;color:#9A7A5A;font-weight:700;margin-bottom:4px;'>"
            "👇 Tap the mic, then say the words!</div>",
            unsafe_allow_html=True,
        )
        inject_mic_listener()
        st.markdown("<div class='mic-ring'>", unsafe_allow_html=True)
        audio_bytes_bd = audio_recorder(
            text="", recording_color="#C17A4A", neutral_color="#BBA890",
            icon_size="3x", pause_threshold=0.7,
            key=f"buildup_{st.session_state.score}_{st.session_state.attempts}_{step_idx}",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if audio_bytes_bd:
            playback_child_voice(audio_bytes_bd)
            recognized_bd, err_bd = try_recognize(audio_bytes_bd)
            if recognized_bd:
                if is_correct(recognized_bd, partial):
                    if is_final:
                        # Full sentence complete!
                        handle_answer(current, st.session_state.category, True, recognized_bd)
                        st.balloons()
                        st.markdown(
                            "<div class='fb-yes'>🎉 You said it ALL! Amazing! 🎉</div>",
                            unsafe_allow_html=True,
                        )
                        if st.button("➡️  Next sentence!", key="buildup_next_final", use_container_width=True):
                            st.session_state.current_word = None
                            st.session_state.feedback = None
                            st.rerun()
                    else:
                        # Advance to next step
                        st.session_state.buildup_step = step_idx + 1
                        next_partial = " ".join(steps[step_idx + 1])
                        st.markdown(
                            f"<div class='fb-yes'>✅ Great! Now say: <b>{next_partial}</b></div>",
                            unsafe_allow_html=True,
                        )
                        st.session_state.pop("buildup_autoplayed", None)
                        st.rerun()
                else:
                    st.session_state.current_word_tries += 1
                    tries_bd = st.session_state.current_word_tries
                    speak_instant(partial)
                    circles_bd = "".join(
                        "🟠" if i < tries_bd else "⚪"
                        for i in range(3)
                    )
                    st.markdown(
                        f"<div class='fb-no'>Almost! Say: <b style='color:#C17A4A;'>{partial}</b><br>"
                        f"<span style='font-size:22px;'>{circles_bd}</span></div>",
                        unsafe_allow_html=True,
                    )
                    if tries_bd >= 3:
                        st.session_state.buildup_step = step_idx + 1 if not is_final else step_idx
                        st.session_state.current_word_tries = 0
                        st.rerun()
            elif err_bd == "quiet":
                st.markdown("<div class='fb-no'>🙈 I didn't hear anything! Speak louder! 🌈</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='fb-no'>Oops! Try again! 🌈</div>", unsafe_allow_html=True)

        c1b, c2b, c3b = st.columns([1, 2, 1])
        with c2b:
            if st.button("⏭️  Skip sentence", use_container_width=True, key="buildup_skip"):
                st.session_state.current_word = None
                st.session_state.feedback = None
                st.rerun()
        st.stop()
    # ── End Sentence Build-Up ─────────────────────────────────────────────────

    # Lock in the current word for this turn — only advance when explicitly requested
    if st.session_state.current_word is None:
        st.session_state.current_word = pick_next_word()
        st.session_state.pop("last_autoplayed", None)  # force auto-play for new word
    current = st.session_state.current_word

    # Auto-speak the word with countdown when it first appears (Echo Mode)
    if st.session_state.get("last_autoplayed") != current["text"]:
        speak_then_record(current["text"])
        st.session_state.last_autoplayed = current["text"]

    txt_len = len(current['text'])
    txt_size = "26px" if txt_len > 20 else "36px" if txt_len > 10 else "48px"
    txt_spacing = "0px" if txt_len > 10 else "3px"
    syllable_hint = SYLLABLES.get(current["text"].lower(), "")
    syllable_html = (
        f"<div style='font-size:17px;color:#B08060;letter-spacing:3px;margin-top:4px;font-weight:600;'>"
        f"{syllable_hint}</div>"
    ) if syllable_hint else ""
    st.markdown(f"""
    <div class='word-card'>
        <div class='word-emoji'>{current['emoji']}</div>
        <div class='word-text' style='font-size:{txt_size};letter-spacing:{txt_spacing};'>{current['text'].capitalize()}</div>
        {syllable_html}
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔊  Hear it!", use_container_width=True, key="practice_hear"):
            speak_instant(current["text"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;font-size:17px;color:#9A7A5A;font-weight:700;margin-bottom:4px;'>"
        "👇 Tap the mic, then say the word!</div>",
        unsafe_allow_html=True,
    )
    inject_mic_listener()
    st.markdown("<div class='mic-ring'>", unsafe_allow_html=True)
    audio_bytes = audio_recorder(
        text="", recording_color="#C17A4A", neutral_color="#BBA890",
        icon_size="3x", pause_threshold=0.7,
        key=f"practice_{st.session_state.category}_{st.session_state.score}_{st.session_state.attempts}",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if audio_bytes:
        playback_child_voice(audio_bytes)
        recognized, err = try_recognize(audio_bytes)
        if recognized:
            handle_answer(current, st.session_state.category, is_correct(recognized, current["text"]), recognized)
        elif err == "quiet":
            st.markdown(
                "<div class='fb-no'>🙈 I didn't hear anything!<br>"
                "Tap the mic and speak a little louder! 🌈</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<div class='fb-no'>Oops! Try again! 🌈</div>", unsafe_allow_html=True)

    if st.session_state.feedback:
        kind, heard = st.session_state.feedback
        if kind == "correct":
            st.markdown(f"<div class='celebrate-emoji'>{current['emoji']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='fb-yes'>🎉 YES! {current['text'].capitalize()}! 🎉</div>", unsafe_allow_html=True)
        else:
            # Auto-replay the word and show encouragement
            speak_instant(current["text"])
            tries = st.session_state.current_word_tries
            encouragements = [
                "Almost! You can do it! 💪",
                "So close! Try one more time! 🌟",
                "Keep going, superstar! ⭐",
                "Nearly there! Give it another go! 🌈",
            ]
            enc = encouragements[st.session_state.attempts % len(encouragements)]
            # 3-attempt circles
            circles = "".join(
                "<span style='font-size:24px;'>🟠</span>" if i < tries else "<span style='font-size:24px;color:#DDD;'>⚪</span>"
                for i in range(3)
            )
            st.markdown(
                f"<div class='fb-no'>{enc}<br>"
                f"<span style='font-size:42px;font-weight:900;color:#C17A4A;'>"
                f"{current['emoji']} {current['text'].capitalize()}</span><br>"
                f"<div style='margin-top:8px;'>{circles}</div></div>",
                unsafe_allow_html=True,
            )
            # After 3 wrong tries, auto-advance
            if tries >= 3:
                st.markdown(
                    "<div style='text-align:center;font-size:22px;color:#9A7A5A;margin-top:6px;'>"
                    "Let's come back to this one! 💪</div>",
                    unsafe_allow_html=True,
                )
                st.session_state.feedback     = None
                st.session_state.current_word = None
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("➡️  Next word!", use_container_width=True, key="practice_next"):
            st.session_state.feedback     = None
            st.session_state.current_word = None
            st.rerun()
    with c3:
        if st.button("⏭️  Skip", use_container_width=True, key="practice_skip"):
            st.session_state.feedback     = None
            st.session_state.current_word = None
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# FLUSH PERSISTENCE
# ══════════════════════════════════════════════════════════════════════════════
flush_progress()
