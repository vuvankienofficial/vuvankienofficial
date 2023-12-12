import telebot
from telebot import types
import time
import re
import threading

TOKEN = '6139863601:AAEFnUE47SJKEo2Gf9V3rUZXRo5AZU-c66E'
bot = telebot.TeleBot(TOKEN)
import logging
logging.basicConfig(level=logging.DEBUG)
user_id = 5802040566
group_id = -4027556693

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    is_admin = (user_id == user_id)

    if is_admin:
        # Kiểm tra xem tin nhắn có chứa lệnh nào đó không
        if message.caption and message.caption.startswith('/sen'):
            # Lấy thông tin ảnh có độ phân giải cao nhất
            photo = message.photo[-1]
            photo_file_id = photo.file_id
            caption = message.caption

            # Extract button information using parentheses
            button_infos = re.findall(r'\((.*?)\)', caption)
            buttons = []
            for button_info in button_infos:
                button_data = button_info.split('|')
                if len(button_data) >= 2:
                    button_url, button_name = button_data[0], button_data[1]
                    button = types.InlineKeyboardButton(button_name, url=button_url)
                    buttons.append(button)

            # Tạo hàng nút với các nút được tạo
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            # Lấy nội dung text từ tin nhắn bỏ qua phần lệnh và các button
            text_content = ' '.join(message.caption.split(' ')[1:]) if message.caption else ''

            # Loại bỏ nội dung của các button từ text_content
            for button_info in button_infos:
                text_content = text_content.replace(f'({button_info})', '')

            # Chuyển tiếp ảnh đến nhóm với nút và chỉ chứa nội dung text không chứa nội dung của button trong caption
            bot.send_photo(group_id, photo_file_id, caption=text_content, reply_markup=keyboard, parse_mode='HTML')

def extract_buttons(text):
    # Tìm tất cả các đoạn văn bản trong ngoặc đơn chứa các nút
    button_matches = re.finditer(r'\((.*?)\)', text)
    buttons = []

    for match in button_matches:
        button_data = match.group(1).split('|')
        if len(button_data) >= 2:
            button_url, button_name = button_data[0], button_data[1]
            button = types.InlineKeyboardButton(button_name, url=button_url)
            buttons.append(button)

    return buttons

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    is_admin = (user_id == user_id)

    if is_admin:
        # Kiểm tra xem có lệnh /chat không và tin nhắn bắt đầu bằng /chat
        if message.text and message.text.startswith('/chat'):
            # Lấy thời gian trễ từ tin nhắn (nếu có)
            delay_match = re.search(r'\((\d+)\)', message.text)
            delay_seconds = int(delay_match.group(1)) if delay_match else 0

            # Xử lý tin nhắn văn bản bắt đầu bằng "/chat"
            # Loại bỏ "/chat" và thời gian trễ từ tin nhắn
            chat_text = message.text.replace('/chat', '', 1).strip()

            # Gửi tin nhắn sau khi loại bỏ "/chat" và chờ độ trễ
            time.sleep(delay_seconds)

            # Extract buttons from the message text
            buttons = extract_buttons(chat_text)

            # Tạo hàng nút với các nút được tạo
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            # Lấy nội dung text từ tin nhắn bỏ qua phần lệnh và các button
            text_content = re.sub(r'\(.*?\)', '', chat_text).strip()

            # Gửi tin nhắn văn bản và button nếu có
            if buttons:
                bot.send_message(group_id, text_content, reply_markup=keyboard, parse_mode='HTML')
            else:
                bot.send_message(group_id, text_content, parse_mode='HTML')

if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling()