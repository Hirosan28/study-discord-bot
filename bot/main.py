import discord # Discord.py of library
import os #　Need to import api and key

from fpdf import FPDF # Text to PDF conversion

import base64 # Convert image
from openai import OpenAI # openAIを利用するため

# Get a environment variable in .env to docker-compose.yaml
TOKEN = os.getenv("TOKEN")
OpenAIkey = os.getenv("OpenAIkey")

# Work a discord bot
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

@client.event
async def on_message(messages):
    if messages.content == "test": # If you post messages "test"
        print("ok")

        # Identify images
        if messages.attachments:
            for attachment in messages.attachments:
                if attachment.content_type.startswith("image"):
                    # Download images
                    await attachment.save(f"./{attachment.filename}")
                    IMAGE_PATH = f"./{attachment.filename}"

        # Convert image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        
        base64_image = encode_image(IMAGE_PATH)

        # Set a model
        MODEL="gpt-4o"

        # Get a openai key
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", OpenAIkey))
        
        # Setting your prompt
        completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "あなたは最高の高校教師です。写真の問題の全ての回答と解説をしたレポートを書いてください。"}, 
            {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
        ]}]
        )

        # Make a PDF
        pdf = FPDF()
        pdf.add_page()

        # Setting Japanese font
        font_path =r"./yugothib.ttf"
        pdf.add_font("yugothib",fname=font_path,uni=True)
        pdf.set_font("yugothib", size=12)
        
        # The text
        text = completion.choices[0].message.content
        pdf.multi_cell(0, 10, txt=text, align="L")

        # Download PDF
        pdf.output("output.pdf")

        # Post your channel
        await messages.channel.send(file=discord.File('./output.pdf', filename='aaa.pdf'))        

# Run discord bot
client.run(TOKEN)
