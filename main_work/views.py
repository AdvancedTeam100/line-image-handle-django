from django.shortcuts import render
from django.http import HttpResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
import torch
import clip
from PIL import Image
import os

# Set up your LINE Bot credentials
channel_secret = 'YOUR_CHANNEL_SECRET'
channel_access_token = 'YOUR_CHANNEL_ACCESS_TOKEN'

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# Create your views here.
def create_upload(request):
    return HttpResponse("Welcome to main work")

def callback(request):
    signature = request.headers['X-Line-Signature']
    body = request.body.decode('utf-8')

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponse(status=400)

    return HttpResponse(status=200)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    image_message = event.message
    image_content = line_bot_api.get_message_content(image_message.id)

    content_type = image_content.headers['Content-Type']
    if not content_type.startswith('image'):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='画像の受け取りに失敗しました')
        )
        return

    # Save the image locally
    filename = f"image_{image_message.id}.jpg"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, 'wb') as f:
        for chunk in image_content.iter_content():
            f.write(chunk)

    # Compare the saved image with another image and send the result to LINE
    result = compare_images_and_send_result(filepath, 'path/to/second/image.jpg', 'cool')
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )

def compare_images_and_send_result(image1_file, image2_file, text):
    # Load the CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Prepare the images and text
    image1 = preprocess(Image.open(image1_file)).unsqueeze(0).to(device)
    image2 = preprocess(Image.open(image2_file)).unsqueeze(0).to(device)
    tokenized_text = clip.tokenize(text).to(device)
    
    with torch.no_grad():
        # Encode the images and text
        image1_features = model.encode_image(image1)
        image2_features = model.encode_image(image2)
        text_features = model.encode_text(tokenized_text)
        
        # Calculate the similarities
        image1_text_similarity = (image1_features @ text_features.T).item()
        image2_text_similarity = (image2_features @ text_features.T).item()
        
        # Determine which image is more similar to the text
        if image1_text_similarity > image2_text_similarity:
            result = f"{image1_file} wins!"
        else:
            result = f"{image2_file} wins!"
        
        return result
