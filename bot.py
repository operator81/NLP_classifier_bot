import pickle
import subprocess
import tempfile
import os
from pathlib import Path

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import speech_recognition as sr

# пути к файлам
way = "путь расположения папки с ботом" #___________________________ вставить путь к папке с проектом
model_file = way + "/model.pkl"
vec_file = way + "/vectorizer.pkl"
ffmpeg_file = way + "/ffmpeg.exe"
token = "токен"                       #______________________________ ВСТАВИТЬ   ТОКЕН   ОТ   ТЕЛЕГРАМММА

# загрузка модели
print("загрузка модели...")
with open(model_file, "rb") as f:
    model = pickle.load(f)
with open(vec_file, "rb") as f:
    vectorizer = pickle.load(f)
print("готово")

# словарь
sentiments = ["негативный", "нейтральный", "позитивный"]

def analyze(text):
    if text == "":
        return "пусто"
    
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    return sentiments[pred]

# работа с телеграмм

def start(update, context):
    update.message.reply_text("привет! отправь отзыв о кафе или ресторане")

def text_message(update, context):
    text = update.message.text
    res = analyze(text)
    update.message.reply_text(res)

def voice_message(update, context):
    try:
        # работа с голосом
        voice = update.message.voice
        file = context.bot.get_file(voice.file_id)    
        temp = tempfile.mkdtemp()
        ogg_file = temp + "/voice.ogg"
        wav_file = temp + "/voice.wav"
        file.download(ogg_file)
        
        # конвертация FFMPEG
        cmd = [ffmpeg_file, "-i", ogg_file, "-ar", "16000", "-ac", "1", wav_file]
        subprocess.run(cmd, check=True)
        
        # распознание речи
        r = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="ru-RU")
        
        # оценка сообщения
        res = analyze(text)
        update.message.reply_text(f"текст: {text}\nоценка: {res}")
        
        os.remove(ogg_file)
        os.remove(wav_file)
        os.rmdir(temp)
        
    except:
        update.message.reply_text("ошибка при обработке голоса")

def main():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, text_message))
    dp.add_handler(MessageHandler(Filters.voice, voice_message))
       
    print("бот запущен")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()