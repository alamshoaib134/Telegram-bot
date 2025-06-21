import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import openai
from openai import OpenAI



# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
OPENAI_TOKEN = "OPENAI_TOKEN"


client = OpenAI("CONFIGUURE YOUR OPENAI")



# Available moods with emojis
MOODS = {
    'happy': '😊 Happy',
    'sad': '😢 Sad',
    'angry': '😠 Angry',
    'excited': '🤩 Excited',
    'anxious': '😰 Anxious',
    'bored': '😴 Bored',
    'confused': '🤔 Confused',
    'grateful': '🙏 Grateful',
    'frustrated': '😤 Frustrated',
    'calm': '😌 Calm',
    'energetic': '⚡ Energetic',
    'melancholic': '😔 Melancholic',
    'optimistic': '🌟 Optimistic',
    'stressed': '😵 Stressed',
    'playful': '😜 Playful'
}

# Store user data (in production, use a proper database)
user_data = {}

class TelegramAIBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("mood", self.mood_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("introvert", self.introvert_command))
        self.application.add_handler(CommandHandler("dsa", self.dsa_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_mood_selection))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Welcome to the AI Mood Bot! 

I can provide personalized suggestions, jokes, and advice based on your current mood.

Available commands:
/mood - Select your current mood and get AI suggestions
/help - Show this help message

Let's start by checking your mood! Use /mood command.
        """
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
    🆘 **Help & Commands**

    /start - Welcome message and introduction
    /mood - Select your current mood and get personalized AI response
    /introvert - Get conversation starters for different social situations
    /dsa - Practice Data Structures & Algorithms with interactive problems
    /help - Show this help message

    **How it works:**
    1. Use /mood command to get mood-based suggestions
    2. Use /introvert to get conversation openers for social situations
    3. Use /dsa to practice coding problems with solutions
    4. Select your preferred options and get personalized content

    The AI will provide different types of responses based on your selections!
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')

    async def mood_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mood command - show mood selection keyboard"""
        keyboard = []
        mood_items = list(MOODS.items())
        
        # Create keyboard with 2 buttons per row
        for i in range(0, len(mood_items), 2):
            row = []
            for j in range(2):
                if i + j < len(mood_items):
                    mood_key, mood_display = mood_items[i + j]
                    row.append(InlineKeyboardButton(
                        mood_display, 
                        callback_data=f"mood_{mood_key}"
                    ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎭 How are you feeling right now? Select your mood:",
            reply_markup=reply_markup
        )

    async def handle_mood_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mood selection from inline keyboard"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("mood_"):
            mood = query.data.replace("mood_", "")
            user_id = query.from_user.id
            
            # Store user mood
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['current_mood'] = mood
            
            # Show loading message
            await query.edit_message_text(
                f"You selected: {MOODS[mood]}\n\n🤖 Let me think of something perfect for your mood..."
            )
            
            # Generate AI response
            ai_response = await self.generate_ai_response(mood, query.from_user.first_name)
            
            # Send AI response
            await query.edit_message_text(
                f"**Your mood:** {MOODS[mood]}\n\n{ai_response}\n\n"
                f"💡 Use /mood anytime to update your mood and get new suggestions!"
            )

    async def introvert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /introvert command - show conversation style options"""
        keyboard = []
        
        # Define conversation styles with emojis
        conversation_styles = {
            'casual': '🙂 Casual',
            'playful': '😜 Playful',
            'compliment': '✨ Compliment',
            'intellectual': '🧠 Intellectual',
            'humor': '😂 Humor',
            'sarcasm': '😏 Sarcasm',
            'curious': '🤔 Curious',
            'empathetic': '💗 Empathetic',
            'shared_interest': '🔍 Shared Interest',
            'situational': '📍 Situational',
            'professional': '👔 Professional'
        }
        
        style_items = list(conversation_styles.items())
        
        # Create keyboard with 2 buttons per row
        for i in range(0, len(style_items), 2):
            row = []
            for j in range(2):
                if i + j < len(style_items):
                    style_key, style_display = style_items[i + j]
                    row.append(InlineKeyboardButton(
                        style_display, 
                        callback_data=f"convo_{style_key}"
                    ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💬 *Conversation Opener Styles*\n\nSelect a conversation style for meeting new people:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_mood_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle mood selection from inline keyboard"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("mood_"):
            # Existing mood handling code
            mood = query.data.replace("mood_", "")
            user_id = query.from_user.id
            
            # Store user mood
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['current_mood'] = mood
            
            # Show loading message
            await query.edit_message_text(
                f"You selected: {MOODS[mood]}\n\n🤖 Let me think of something perfect for your mood..."
            )
            
            # Generate AI response
            ai_response = await self.generate_ai_response(mood, query.from_user.first_name)
            
            # Send AI response
            await query.edit_message_text(
                f"**Your mood:** {MOODS[mood]}\n\n{ai_response}\n\n"
                f"💡 Use /mood anytime to update your mood and get new suggestions!"
            )
        
        elif query.data.startswith("convo_"):
            style = query.data.replace("convo_", "")
            
            # Show loading message
            await query.edit_message_text(
                f"Creating conversation openers with {style} style...\n\n🤖 Thinking..."
            )
            
            # Generate conversation openers
            openers = await self.generate_conversation_openers(style)
            
            # Send openers
            await query.edit_message_text(
                f"🗣️ *{style.capitalize()} Conversation Openers*\n\n{openers}\n\n"
                f"💡 Use /introvert anytime to get new conversation ideas!"
            )
    
    async def generate_conversation_openers(self, style: str) -> str:
        """Generate conversation openers based on selected style"""
        
        # Style-specific prompts
        style_prompts = {
            'casual': "Generate 3 casual, friendly conversation starters for an introvert to use when meeting new people. These should be low-pressure, natural openers that don't feel forced.",
            'playful': "Generate 3 playful, light-hearted conversation starters for an introvert to use when meeting new people. These should be fun but not too forward.",
            'compliment': "Generate 3 genuine, non-creepy compliment-based conversation starters for an introvert to use when meeting new people. Focus on noticing something interesting rather than physical appearance.",
            'intellectual': "Generate 3 thought-provoking, intellectual conversation starters for an introvert to use when meeting new people. These should invite interesting discussions.",
            'humor': "Generate 3 humorous, witty conversation starters for an introvert to use when meeting new people. These should be light and universally appealing.",
            'sarcasm': "Generate 3 mildly sarcastic but friendly conversation starters for an introvert to use when meeting new people. These should be witty but not offensive.",
            'curious': "Generate 3 curious, question-based conversation starters for an introvert to use when meeting new people. These should show genuine interest without being too personal.",
            'empathetic': "Generate 3 empathetic, understanding conversation starters for an introvert to use when meeting new people. These should create connection through shared human experiences.",
            'shared_interest': "Generate 3 conversation starters based on potential shared interests for an introvert to use when meeting new people. These should help identify common ground.",
            'situational': "Generate 3 situational conversation starters for an introvert to use when meeting new people in common settings (coffee shop, event, etc). These should reference the shared environment.",
            'professional': "Generate 3 professional, networking-appropriate conversation starters for an introvert to use when meeting new people in a work context. These should be respectful and career-oriented."
        }
        
        try:
            prompt = style_prompts.get(style, "Generate 3 natural, friendly conversation starters for an introvert to use when meeting new people.")

            response = client.chat.completions.create(
                model="databricks-meta-llama-3-1-8b-instruct",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant providing conversation starters for introverts. Your suggestions should be respectful, practical, and effective for social situations. Format each opener with a bullet point and add a brief explanation of why it works well."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation openers: {e}")
            return self.get_fallback_conversation_openers(style)

    def get_fallback_conversation_openers(self, style: str) -> str:
        """Fallback conversation openers when AI is unavailable"""
        fallback_openers = {
            'casual': "• \"I'm trying that coffee for the first time - is it any good?\"\n• \"This place/event has such a unique vibe. Have you been here before?\"\n• \"I noticed your book/bag/item - that's really cool. Where did you find it?\"",
            'playful': "• \"If you were a superhero, what would your completely useless superpower be?\"\n• \"I'm conducting an informal survey - pineapple on pizza: brilliant or criminal offense?\"\n• \"I'm trying to settle a debate with my friend - what's the correct way to pronounce GIF?\"",
            'compliment': "• \"I couldn't help but notice your (item) - you have great taste!\"\n• \"That was a really insightful comment you made earlier about (topic).\"\n• \"I like your energy - you seem like someone who really enjoys what they do.\"",
            'intellectual': "• \"I just read an article about (current event). What's your take on it?\"\n• \"If you could have dinner with any historical figure, who would you choose?\"\n• \"What book or podcast has influenced your thinking the most recently?\"",
            'humor': "• \"I was going to tell a joke about time travel, but you didn't like it.\"\n• \"I'm practicing my small talk skills today. How am I doing so far? Be honest!\"\n• \"I'm terrible with names, so I'm just mentally calling you 'potential new friend' - unless you'd prefer something else?\"",
            'sarcasm': "• \"Another exciting day in paradise, right? What's been the highlight so far?\"\n• \"I see you also made the brave choice to socialize today. How's that working out?\"\n• \"Let me guess, you're here for the amazing free coffee too?\"",
            'curious': "• \"What brings you to this event/place today?\"\n• \"I'm curious - what do you enjoy most about what you do?\"\n• \"I'm exploring new interests lately. What's something you're passionate about?\"",
            'empathetic': "• \"These kinds of events can be a bit overwhelming sometimes. How are you finding it?\"\n• \"It took me three attempts to actually come in today. Do you ever find social situations a bit challenging too?\"\n• \"I think everyone here is pretending to be more comfortable than they really are. What do you think?\"",
            'shared_interest': "• \"I noticed you're [reading that book/using that app/wearing that band shirt]. I'm a fan too! What do you think of it?\"\n• \"Are you following the latest season of [popular show]? I've been hooked!\"\n• \"This [food/drink/music] is fantastic. Are you also into [related interest]?\"",
            'situational': "• \"The organizers really went all out with this event. What do you think of it so far?\"\n• \"I've been trying to figure out what that interesting painting over there represents. Any ideas?\"\n• \"I'm new to this [class/group/event]. Have you been coming here long?\"",
            'professional': "• \"I found the point about [topic from presentation/meeting] really interesting. What's your take on it?\"\n• \"What projects are you working on currently that you're excited about?\"\n• \"How did you get started in this industry? I'd love to hear about your path.\""
        }
        
        return fallback_openers.get(style, "• \"Hi, I'm [your name]. What brings you here today?\"\n• \"I like your [item/accessory]. Is there a story behind it?\"\n• \"I'm new to this [event/place/group]. Do you have any recommendations?\"")

    async def generate_ai_response(self, mood: str, user_name: str = "there") -> str:
        """Generate AI response based on user's mood"""
        
        # Mood-specific prompts
        mood_prompts = {
            'happy': f"The user {user_name} is feeling happy! Give them a cheerful joke, fun activity suggestion, or positive affirmation to keep their good vibes going.",
            'sad': f"The user {user_name} is feeling sad. Provide gentle comfort, uplifting words, or a small activity that might help brighten their day.",
            'angry': f"The user {user_name} is feeling angry. Suggest healthy ways to manage anger, calming techniques, or perspective-shifting thoughts.",
            'excited': f"The user {user_name} is feeling excited! Share in their enthusiasm with energetic suggestions or ways to channel their excitement productively.",
            'anxious': f"The user {user_name} is feeling anxious. Provide calming techniques, reassuring words, or grounding exercises to help them feel more at ease.",
            'bored': f"The user {user_name} is feeling bored. Suggest interesting activities, fun challenges, or creative projects they could try.",
            'confused': f"The user {user_name} is feeling confused. Offer clarity-building techniques, suggest taking a step back, or provide encouraging words about working through confusion.",
            'grateful': f"The user {user_name} is feeling grateful! Help them amplify this positive feeling with gratitude exercises or ways to spread kindness.",
            'frustrated': f"The user {user_name} is feeling frustrated. Suggest patience-building techniques, problem-solving approaches, or stress-relief activities.",
            'calm': f"The user {user_name} is feeling calm. Help them maintain this peaceful state with mindfulness suggestions or reflective activities.",
            'energetic': f"The user {user_name} is feeling energetic! Suggest productive ways to use this energy or fun physical activities.",
            'melancholic': f"The user {user_name} is feeling melancholic. Provide gentle understanding and suggest comforting activities or creative outlets.",
            'optimistic': f"The user {user_name} is feeling optimistic! Encourage this positive outlook with goal-setting ideas or ways to spread positivity.",
            'stressed': f"The user {user_name} is feeling stressed. Provide stress-relief techniques, relaxation methods, or perspective on managing stress.",
            'playful': f"The user {user_name} is feeling playful! Suggest fun games, silly jokes, or creative activities that match their playful energy."
        }
        
        try:
            prompt = mood_prompts.get(mood, f"The user {user_name} is in a {mood} mood. Provide appropriate suggestions or encouragement.")

            response = client.chat.completions.create(
                model="databricks-meta-llama-3-1-8b-instruct",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful, empathetic AI assistant that provides personalized suggestions, jokes, and advice based on people's moods. Keep responses concise (2-3 sentences), warm, and actionable. Use appropriate emojis."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self.get_fallback_response(mood)

    def get_fallback_response(self, mood: str) -> str:
        """Fallback responses when AI is unavailable"""
        fallback_responses = {
            'happy': "🌟 That's wonderful! Keep spreading those positive vibes! Maybe share your happiness with someone special today.",
            'sad': "💙 I'm sorry you're feeling down. Remember, it's okay to feel sad sometimes. Consider taking a warm bath or calling a friend.",
            'angry': "🌊 Take a deep breath. Try counting to 10 or going for a quick walk to help cool down. You've got this!",
            'excited': "🎉 Your excitement is contagious! Channel that energy into something creative or share the good news with someone!",
            'anxious': "🕯️ Breathe slowly and deeply. Try the 5-4-3-2-1 grounding technique: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            'bored': "🎨 Time for something new! Try learning a fun fact, doodling, or rearranging your space for a fresh perspective.",
            'confused': "🧩 It's okay to feel confused. Take a step back, write down your thoughts, or talk it through with someone you trust.",
            'grateful': "🙏 Gratitude is beautiful! Consider writing down three things you're thankful for or telling someone how much they mean to you.",
            'frustrated': "⚡ Frustration shows you care! Take a short break, do some stretches, or try approaching the problem from a different angle.",
            'calm': "🧘 Enjoy this peaceful moment! Maybe try some light meditation or simply savor the tranquility you're feeling.",
            'energetic': "🏃 Great energy! Use it for a workout, cleaning, dancing, or tackling that task you've been putting off!",
            'melancholic': "🌙 Sometimes we need these reflective moments. Consider journaling, listening to music, or creating something artistic.",
            'optimistic': "✨ Your positive outlook is powerful! Set a small goal for today or do something kind for someone else.",
            'stressed': "🌱 Stress happens to everyone. Try deep breathing, gentle stretching, or breaking big tasks into smaller, manageable steps.",
            'playful': "🎪 Love the playful energy! Try a silly dance, make funny faces in the mirror, or play a quick game!"
        }
        
        return fallback_responses.get(mood, "Thanks for sharing your mood with me! Remember, all feelings are valid and temporary. 💫")

    async def dsa_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dsa command - show DSA topic selection keyboard"""
        keyboard = []
        
        # Define DSA topics with emojis
        dsa_topics = {
            'arrays': '📊 Arrays',
            'linked_lists': '⛓️ Linked Lists',
            'stacks_queues': '📚 Stacks & Queues',
            'trees': '🌳 Trees & BST',
            'graphs': '🕸️ Graphs',
            'hash_tables': '🔍 Hash Tables',
            'heaps': '⛰️ Heaps',
            'sorting': '📋 Sorting',
            'searching': '🔎 Searching',
            'dynamic_programming': '📈 Dynamic Programming',
            'greedy': '🤑 Greedy Algorithms',
            'bit_manipulation': '🔢 Bit Manipulation',
            'recursion': '🔄 Recursion',
            'backtracking': '↩️ Backtracking',
            'random': '🎲 Random Question'
        }
        
        topic_items = list(dsa_topics.items())
        
        # Create keyboard with 2 buttons per row
        for i in range(0, len(topic_items), 2):
            row = []
            for j in range(2):
                if i + j < len(topic_items):
                    topic_key, topic_display = topic_items[i + j]
                    row.append(InlineKeyboardButton(
                        topic_display, 
                        callback_data=f"dsa_{topic_key}"
                    ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "💻 *Data Structures & Algorithms Practice*\n\nSelect a topic to get a practice question with solution:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_mood_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle selections from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("mood_"):
            # Existing mood handling code
            mood = query.data.replace("mood_", "")
            user_id = query.from_user.id
            
            # Store user mood
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['current_mood'] = mood
            
            # Show loading message
            await query.edit_message_text(
                f"You selected: {MOODS[mood]}\n\n🤖 Let me think of something perfect for your mood..."
            )
            
            # Generate AI response
            ai_response = await self.generate_ai_response(mood, query.from_user.first_name)
            
            # Send AI response
            await query.edit_message_text(
                f"**Your mood:** {MOODS[mood]}\n\n{ai_response}\n\n"
                f"💡 Use /mood anytime to update your mood and get new suggestions!"
            )
        
        elif query.data.startswith("convo_"):
            style = query.data.replace("convo_", "")
            
            # Show loading message
            await query.edit_message_text(
                f"Creating conversation openers with {style} style...\n\n🤖 Thinking..."
            )
            
            # Generate conversation openers
            openers = await self.generate_conversation_openers(style)
            
            # Send openers
            await query.edit_message_text(
                f"🗣️ *{style.capitalize()} Conversation Openers*\n\n{openers}\n\n"
                f"💡 Use /introvert anytime to get new conversation ideas!"
            )
            
        elif query.data.startswith("dsa_"):
            topic = query.data.replace("dsa_", "")
            
            # Show loading message
            await query.edit_message_text(
                f"Preparing a {'random' if topic == 'random' else topic} DSA question...\n\n🤖 Thinking..."
            )
            
            # Generate DSA question and solution
            question_solution = await self.generate_dsa_question(topic)
            
            # Send question and solution
            await query.edit_message_text(
                f"🧩 *DSA Practice: {topic.replace('_', ' ').title()}*\n\n{question_solution}\n\n"
                f"💡 Use /dsa anytime to practice more questions!",
                parse_mode='Markdown'
            )
    
    async def generate_dsa_question(self, topic: str) -> str:
      """Generate a DSA question and solution based on selected topic"""
          
        # If random topic is selected, choose a random topic
      if topic == 'random':
            import random
            topics = ['arrays', 'linked_lists', 'stacks_queues', 'trees', 'graphs', 
                    'hash_tables', 'heaps', 'sorting', 'searching', 'dynamic_programming',
                    'greedy', 'bit_manipulation', 'recursion', 'backtracking']
            topic = random.choice(topics)
        
        # Topic-specific prompts
      topic_prompts = {
            'arrays': "Generate a medium difficulty array algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'linked_lists': "Generate a medium difficulty linked list algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'stacks_queues': "Generate a medium difficulty stack or queue algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'trees': "Generate a medium difficulty binary tree or BST algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'graphs': "Generate a medium difficulty graph algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'hash_tables': "Generate a medium difficulty hash table/dictionary algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'heaps': "Generate a medium difficulty heap/priority queue algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'sorting': "Generate a medium difficulty sorting algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'searching': "Generate a medium difficulty searching algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'dynamic_programming': "Generate a medium difficulty dynamic programming problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'greedy': "Generate a medium difficulty greedy algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'bit_manipulation': "Generate a medium difficulty bit manipulation problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'recursion': "Generate a medium difficulty recursion problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.",
            'backtracking': "Generate a medium difficulty backtracking problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity."
        }
        
      try:
            prompt = topic_prompts.get(topic, "Generate a medium difficulty algorithm problem. Include the problem statement, example input/output, and a detailed solution with Python code and explanation of time/space complexity.")

            response = client.chat.completions.create(
                model="databricks-meta-llama-3-1-8b-instruct",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a DSA (Data Structures and Algorithms) expert who creates clear, educational coding problems with solutions. Format your response with a clear problem statement first, followed by examples, then a detailed solution with well-commented Python code. End with a brief explanation of the time and space complexity."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
      except Exception as e:
            logger.error(f"Error generating DSA question: {e}")
            return self.get_fallback_dsa_question(topic)
    def get_fallback_dsa_question(self, topic: str) -> str:
        """Fallback DSA question and solution when AI is unavailable, I want to print random question"""
        fallback_questions = {
            'arrays': "ARRAY PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'linked_lists': "LINKED LIST PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'stacks_queues': "STACKS & QUEUES PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'trees': "TREES PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'graphs': "GRAPHS PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'hash_tables': "HASH TABLES PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'heaps': "HEAPS PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'sorting': "SORTING PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'searching': "SEARCHING PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'dynamic_programming': "DYNAMIC PROGRAMMING PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'greedy': "GREEDY ALGORITHMS PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'bit_manipulation': "BIT MANIPULATION PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'recursion': "RECURSION PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.",
            'backtracking': "BACKTRACKING PROBLEM IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER."
        }
        return fallback_questions.get(topic, "DSA QUESTION IS NOT AVAILABLE RIGHT NOW, PLEASE TRY AGAIN LATER.")
        

    

    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram AI Mood Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Main execution
if __name__ == '__main__':
    # Create .env file with your tokens
    bot = TelegramAIBot()
    bot.run()