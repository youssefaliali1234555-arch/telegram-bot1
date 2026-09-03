import os
import requests
import telebot

TELEGRAM_BOT_TOKEN = "8464000828:AAGjY2AnmaYtwk0BR2TA6q4NXcRVrEBhvT8"
GEMINI_API_KEY = "AQ.Ab8RN6IHiS4rzs4iiu29e_tbZQ0saNHAIUGCNPeqqI_yYwN_8w"
SHORT_LINK = "https://shrinkme.click/UlypXVMZ"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
user_usage = {}

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    res = requests.post(url, json=payload, headers=headers, timeout=30)
    data = res.json()
    
    if res.status_code == 200:
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        err = data.get('error', {}).get('message', 'خطأ غير معروف')
        return f"خطأ سيرفر جوجل: {err}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "أهلاً بك! 🤖\n"
        "أنا مساعدك الذكي القائم على الذكاء الاصطناعي.\n"
        "لديك 5 محاولات مجانية يومياً لإجابة أسئلتك."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    user_id = message.from_user.id
    
    if user_id not in user_usage:
        user_usage[user_id] = 5

    if user_usage[user_id] > 0:
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            ai_reply = ask_gemini(message.text)
            user_usage[user_id] -= 1
            reply_msg = f"{ai_reply}\n\n-------------------\n📊 المحاولات المتبقية لك اليوم: {user_usage[user_id]}"
            bot.reply_to(message, reply_msg)
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ: {str(e)}")
    else:
        out_of_points_msg = (
            "❌ انتهت محاولاتك المجانية لهذا اليوم!\n\n"
            "للحصول على 5 محاولات إضافية، اضغط على الرابط التالي لتجديد نقاطك:\n"
            f"🔗 {SHORT_LINK}"
        )
        bot.reply_to(message, out_of_points_msg)

bot.infinity_polling()
