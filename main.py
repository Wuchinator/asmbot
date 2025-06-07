import os
import subprocess
import tempfile
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import asyncio
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN=os.getenv("TOKEN")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Пришли мне C-код, а я верну тебе его ассемблерное представление.")

@dp.message()
async def code_handler(message: Message):
    code = message.text
    if not code:
        await message.reply("Пожалуйста, отправь C-код.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, "input.c")
        object_path = os.path.join(tmpdir, "output.o")

        with open(source_path, "w") as f:
            f.write(code)


        compile_cmd = ["gcc", "-c", source_path, "-o", object_path]
        try:
            subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            await message.reply(f"Ошибка компиляции:\n```\n{e.output.decode()}\n```")

            return
        try:
            asm_output = subprocess.check_output(["objdump", "-d", object_path]).decode()
            if len(asm_output) > 4000:
                asm_output = asm_output[:4000] + "\n\n...(обрезано)"
            await message.reply(f"``` \n{asm_output}\n ```", ParseMode.MARKDOWN)
        except Exception as e:
            await message.reply(f"Ошибка дизассемблирования: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
