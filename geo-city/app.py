from flask import Flask, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
import json

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Now you can use these variables in your script
# print(f"YOUTUBE_API_KEY: {YOUTUBE_API_KEY}")
# print(f"OPENAI_KEY: {OPENAI_KEY}")

# Replace with your actual API key
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def search_youtube_videos(query, max_results=5):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results,
        order='date',  # Or use 'relevance'
        videoEmbeddable='true',  # Ensures video is public and embeddable
        safeSearch='strict'  # Optional: keep it child-safe
    )
    response = request.execute()
    # print(response)

    results = []
    youtubeview = ""
    for item in response['items']:
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        description = item['snippet']['description']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(video_url)

        results.append({
            'title': title,
            'description': description,
            'url': video_url
        })
        youtubeview = youtubeview + ",\n " + video_url

    #return youtubeview[1:]
    return results


# Azure OpenAI Client
client = AzureOpenAI(
    api_key="8ItJheHZ3f23z6dtDql9svrzMzuTvg6k4CIfgYCW9grjnqWrHeP3JQQJ99BEACfhMk5XJ3w3AAAAACOG6zrJ",
    api_version="2024-12-01-preview",
    azure_endpoint="https://eran-manlpx0s-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview"
)


def get_transport_details(city_name, category):
    prompt = f"Provide a summary of the public transportation system in {city_name}, India. Include key details such as types of public transport available (e.g., metro, buses, local trains, auto-rickshaws), major routes or networks, ticketing options (smart cards, apps, paper tickets), timings, connectivity to major areas, and any recent developments or upgrades."
    response = client.chat.completions.create(
        model="gpt-4.1",  # This is your Azure deployment name
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    print(response.choices[0].message.content.strip())

    return response.choices[0].message.content.strip()

def generate_youtubequery(city_name, category):
    prompt = f"Generate a YouTube search query for category '{category}' in the city of '{city_name}' that would return recent and engaging videos."


    response = client.chat.completions.create(
        model="gpt-4.1",  # This is your Azure deployment name
        messages=[
            {"role": "system", "content": "You are an expert travel guide for Indian cities."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    print(response.choices[0].message.content.strip())

    return response.choices[0].message.content.strip()


# GPT function
def generate_city_info(city_name, category):
    # prompt = f"Give a brief and interesting description of the Indian city '{city_name}' including popular attractions, culture, and anything unique."
    # prompt = f"Give a concise and engaging summary in 5 to 7 sentences about the category '{category}' in the city of '{city_name}'. Focus on key highlights, local relevance, and what makes this category unique or interesting in that city. Make it informative, friendly, and suitable for a travel or city-exploration app. Additionally, find and return a direct YouTube video link (not just a search query) that best represents this category in the given city. The youtube video should be recently uploaded and make sure they are not older than 1 month, and likely still available online, informative or visually engaging for travellers, showcasing the actual experience or highlights of the selected category in that city"
    prompt = f"Give a concise and engaging summary in 5 to 7 sentences about the category '{category}' in the city of '{city_name}'. Focus on key highlights, local relevance, and what makes this category unique or interesting in that city. Make it informative, friendly, and suitable for a travel or city-exploration app."


    response = client.chat.completions.create(
        model="gpt-4.1",  # This is your Azure deployment name
        messages=[
            # {"role": "system", "content": "You are an expert travel guide for Indian cities."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

@app.route('/city-info', methods=['GET'])
def city_info():
    city = request.args.get('city')
    category = request.args.get('category')
    if not city:
        return jsonify({'error': 'City name is required'}), 400
    
    if not category:
        return jsonify({'error': 'Category is required'}), 400

    try:
        info = generate_city_info(city, category)
        ysearch = generate_youtubequery(city, category)
        ylinks = search_youtube_videos(ysearch)
        transport_details = get_transport_details(city, category)

        # Convert list to JSON response format
        response = {
            "status": "success",
            "city": city,
            "description": info,
            "youtube_links": ylinks,
            "transport": transport_details
        }
        json_response = json.dumps(response, indent=4)

        #return jsonify({'city': city, 'description': info, 'youtube links': ylinks, 'transport': transport_details})
        return json_response
    except Exception as e:
        response = {
            "status": "failure",
            "error": str(e)
        }
        json_response = json.dumps(response, indent=4)
        #return jsonify({'error': str(e)}), 500
        return json_response, 500

if __name__ == '__main__':
    app.run(debug=True)
