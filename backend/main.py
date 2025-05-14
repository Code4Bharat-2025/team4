from flask import Flask, request, jsonify
import requests, json
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
app = Flask(__name__)
api_url = "https://v1-api.swiftchat.ai/api"
bot_uri = "/bots/0270038149322028/messages"
api_key = "21bda582-e8d0-45bc-bb8b-a5c6c555d176"
VERIFY = False

user_conversion_id = ['uLY7cb5uZmUvoc_phTBc4']

@app.route("/")
def home():
    return "Hello, World!"

@app.route("/api/kluster-webhook",methods=["POST",'GET'])
def query():
    print(request.get_json())
    req_data = request.get_json()
    # print(req_data["text"]["body"])
    to = req_data["from"]
    if req_data["conversation_id"] not in user_conversion_id:
        user = create_user_session(req_data)
        user_conversion_id.append(req_data["conversation_id"])
    else:
        user = get_user_session(req_data)
    print (len(user["user"]["questionsAndAnswers"]))
    if len(user["user"]["questionsAndAnswers"])==0:
        # send_message(to,"Hello "+str(to),type="button")
        sendwelcomemessage(to)
        handle_country_selection(req_data)
        add_question_answer(req_data["conversation_id"], "sads",req_data["message_id"],req_data["timestamp"])
    elif len(user["user"]["questionsAndAnswers"])==1:
        # update_json("country",req_data["text"]["body"],req_data["conversation_id"])
        handle_state_selection(req_data,req_data["button_response"]["body"])
        add_question_answer(req_data["conversation_id"], "Country",req_data["message_id"],req_data["timestamp"])
    elif len(user["user"]["questionsAndAnswers"])==2:
        handle_city_selection(req_data,"IN")
        add_question_answer(req_data["conversation_id"], "State",req_data["message_id"],req_data["timestamp"])
    elif len(user["user"]["questionsAndAnswers"])==3:
        json_response = json.loads(city_info())
        print(type(json_response))
        print(json_response["description"])
        send_message(to,json_response["description"],"text")
        send_message(to,get_video_object(),"text")
    else:
        json_response = json.loads(city_info())
        send_message(to,json_response["description"],"text")
    return jsonify({"success":True})

def update_json(key,value,conversation_id):
    data = read_json()
    for item in data:
        if item.get("user", {}).get("conversation_id") == conversation_id:
            item[key] = value
    write_json(data)
    return data

def read_json(file="data.json"):
    # Open and read the JSON file
    with open('data.json', 'r') as file:
        converstion_master_data = json.load(file)
    return converstion_master_data

def write_json(dictionary):
    with open("data.json", "w") as outfile:
        json.dump(dictionary, outfile,indent=4)

def add_question_answer( conversation_id, question,message_id,timestamp):
    data = read_json()
    new_question = {
        "question": question,
        "message_id": message_id,
        "answer": "",
        "timestamp": timestamp
    }
    for item in data:
        if item.get("user", {}).get("conversation_id") == conversation_id:
            item["user"].setdefault("questionsAndAnswers", []).append(new_question)
            break
    write_json(data)
    return data

def send_message(to,message,type):
    headers = get_header()
    # print(message)
    if isinstance(message,str):
        json = get_response_json(to=to,message=message,type=type)
    else:
        json = message
        json["to"] = to
    response = requests.post(api_url+bot_uri,headers=headers,json=json)
    # print(response.status_code)
    print(response.json())

def sendwelcomemessage(to):
    message = f"""Hello "{ str(to)},
            I am GeoME, your virtual explorer!!
        """
    send_message(to,message,type="text")

def update_answer_for_question(conversation_id, question_text, new_answer):
    data = read_json()
    for item in data:
        if item.get("user", {}).get("conversation_id") == conversation_id:
            for qa in item["user"].get("questionsAndAnswers", []):
                if qa.get("question") == question_text:
                    qa["answer"] = new_answer
                    return data  # Stop after the first match
    write_json(data)
    return data

def get_header():
    headers = {
    'Content-Type': 'application/json',
    "Authorization": "Bearer "+ api_key
    }
    return headers

def get_text_object(message):
    return {"type":"text","text":{"body":message}}

def get_button_text_object(message):
    return {"body":message}

def get_image_object(imageurl="https://media.istockphoto.com/id/519611160/vector/flag-of-india.jpg?s=612x612&w=0&k=20&c=0HueaQHkdGC4Fw87s3DbeTE9Orv3mqHRLce88LV47E4="):
    return {
        "type": 'image',
        "image": { "url": imageurl }
      }

def get_video_object(videourl="https://www.youtube.com/watch?v=4o1XD6-kZQs"):
    return "You can find more about this city here on Youtube URL: " + videourl
    return {
        "type": 'video',
        "video": { "url": videourl }
      }

def get_button_object(question,buttonarray,type):
    buttonlist = []
    print(buttonarray)
    if len(buttonarray)>0:
        for item in buttonarray:
            print(item)
            buttonlist.append(
            {
                "type": 'solid',
                "body":  str(item["name"]),
                "reply": str(item["name"]),
            })
    print(buttonlist)
    if type=='text':
        j = {
        "type": 'button',
        "button": {
            "body": {
                "type": type,
                "text": get_button_text_object(question),
            },
            "buttons": buttonlist
            }
        }
    elif type=='image':
        imageurl="https://media.istockphoto.com/id/519611160/vector/flag-of-india.jpg?s=612x612&w=0&k=20&c=0HueaQHkdGC4Fw87s3DbeTE9Orv3mqHRLce88LV47E4="
        j = {
        "type": 'button',
        "button": {
            "body": {
                "type": type,
                "image":{ "url": imageurl }
            },
            "buttons": buttonlist
            }
        }
    return j

def get_response_json(to,message,type='TEXT'):
    if type=='text':
        res = {"to":to,"type":"text","text":{"body":message}}
    elif type=='image':
        res = {"to":to,
        "type": 'image',
        "image": { "url": "https://media.istockphoto.com/id/519611160/vector/flag-of-india.jpg?s=612x612&w=0&k=20&c=0HueaQHkdGC4Fw87s3DbeTE9Orv3mqHRLce88LV47E4=" }
      }
    elif type=='button':
        res = get_button_object("Please Select Country",buttonarray=message,type="image")
    else:
        return "Invalid Type"
    res["to"] = to
    print(res)
    return res

def get_countries_list():
    # print(api_url+"/regions/countries")
    response = requests.get(api_url+"/regions/countries",verify=VERIFY,headers=get_header())
    # print(response.status_code)
    data = response.json()
    return data["data"]

def get_state_list(country_code):
    response = requests.get(f"{api_url}/regions/states?country_code={country_code}",verify=VERIFY,headers=get_header())
    data = response.json()
    return data["data"]

def get_cities_list(country_code="IN",state_code="MH"):
    response = requests.get(f"{api_url}/regions/cities?country_code={country_code}&state_code={state_code}",verify=VERIFY,headers=get_header())
    data = response.json()
    return data["data"]

def send_country_selection(data):
    countries = get_countries_list()
    country = get_button_object("Please Select a Country",countries,"text")
    return country

def send_state_selection(data,sel_country):
    # countries = get_countries_list()
    # print(countries)
    # for country in countries:
    #     if country.get("name").lower() == sel_country.lower():
    #         country_code = country.get("code")
    state_list = get_state_list("IN")
    state = get_button_object("Please Select a State",state_list,"text")
    return state

def send_city_selection(data,city):
    City_list = [{"name":"Pune"},{"name":"Mumbai"}]
    City = get_button_object("Please Select a City",City_list,"text")
    return City
    country = get_button_object("Please Select a City",city,"text")
    return country

def get_user_session(data):
    if "conversation_id" in data:
        if data["conversation_id"] in user_conversion_id:
            convserstion_data = read_json("data.json")
            for item in convserstion_data:
                print(item)
                if item["user"]["from"]==data["from"] and item["user"]["conversation_id"]==data["conversation_id"]:
                    return item
    else:
        user = create_user_session(data)
        return user
                
def create_user_session(data):
    if "conversation_id" in data and data["conversation_id"] not in user_conversion_id:
        user= {"user": {
                "from": data["from"],
                "to": data["from"],
                "conversation_id":data["conversation_id"],
                "questionsAndAnswers": [
                    {
                    "question": data["text"]["body"],
                    "message_id":data["message_id"],
                    "answer": "",
                    "timestamp":data["timestamp"]
                    }
                ]
                }
                }
        convserstion_data = read_json("data.json")
        convserstion_data.append(user)
        write_json(convserstion_data)
    else:
        user = get_user_session()
    return user

def handle_country_selection(data):
    send_message(data["from"],send_country_selection(data),type="button")

def handle_state_selection(data,sel_county):
    send_message(data["from"],send_state_selection(data,"IN"),type="button")

def handle_city_selection(data,sel_county):
    buttonarray = ["Pune","Mumbai","Nagpur"]
    send_message(data["from"],send_city_selection(data,"IN"),type="button")

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
    # city = request.args.get('city')
    # category = request.args.get('category')
    city = "Pune"
    category = "History"
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)