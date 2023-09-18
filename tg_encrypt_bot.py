# 导入cryptography模块
import telebot
from cryptography.fernet import Fernet
import datetime
import time

# 创建一个telegram机器人对象，用你自己的token替换下面的字符串
bot = telebot.TeleBot("xxxx")

# 创建一个字典，用于存储每个聊天组的密钥和过期时间
keys = {}

# 定义一个函数，用于生成一个随机的密钥
def generate_key():
  return Fernet.generate_key()

# 定义一个函数，用于加密一条消息
def encrypt_message(message, key):
  fernet = Fernet(key)
  return fernet.encrypt(message.encode()).decode()

# 定义一个函数，用于解密一条消息
def decrypt_message(message, key):
  fernet = Fernet(key)
  return fernet.decrypt(message.encode()).decode()

# 定义一个函数，用于检查一个聊天组的密钥是否过期，如果过期则更新密钥和过期时间，并通知所有成员
def check_key_expiration(chat_id):
  global keys
  if chat_id not in keys or time.time() > keys[chat_id][1]:
    key = generate_key()
    expiration = time.time() + 86400 # 设置密钥有效期为1天
    keys[chat_id] = (key, expiration)
    bot.send_message(chat_id, "注意：本聊天组的密钥已更新，请使用以下命令获取新的密钥：\n/get_key")

# 定义一个函数，用于处理/start命令，向用户发送欢迎信息和使用说明
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "你好，我是一个用于加密显示聊天组的对话的机器人。请按照以下步骤使用我：\n1. 邀请我加入你想要加密的聊天组。\n2. 在聊天组中使用/get_key命令获取当前的密钥。\n3. 使用密钥加密你想要发送的消息。\n4. 把加密后的消息发送到聊天组中。\n5. 使用密钥解密你收到的消息。\n注意：每个聊天组的密钥都不同，并且每天都会自动更新。请及时获取最新的密钥。")

# 定义一个函数，用于处理/get_key命令，向用户发送当前聊天组的密钥
@bot.message_handler(commands=['get_key'])
def send_key(message):
  chat_id = message.chat.id
  check_key_expiration(chat_id)
  key = keys[chat_id][0]
  bot.reply_to(message, f"本聊天组的当前密钥为：\n{key.decode()}")

# 定义一个函数，用于处理普通消息，向用户发送加密或解密后的消息
@bot.message_handler(func=lambda message: True)
def echo_message(message):
  chat_id = message.chat.id
  check_key_expiration(chat_id)
  key = keys[chat_id][0]
  text = message.text
  try:
    # 尝试解密消息，并在前面加上[解密]标签
    decrypted_text = decrypt_message(text, key)
    bot.reply_to(message, f"[解密] {decrypted_text}")
  except:
    # 如果解密失败，说明消息不是加密过的，那么就尝试加密消息，并在前面加上[加密]标签
    encrypted_text = encrypt_message(text, key)
    bot.reply_to(message, f"[加密] {encrypted_text}")

# 启动机器人
bot.polling()
