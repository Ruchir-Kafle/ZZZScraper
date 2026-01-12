import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json

# getting html page
if Path("cache.html").is_file():
    # retrieving from cache
    with open("cache.html", "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    
    print("soup retrieved from cache")
else:
    # scrape site
    URL = "https://zenless-zone-zero.fandom.com/wiki/Wise/Dialogue"

    response = requests.get(URL)
    print(f"response: {response}")

    content = response.text
    
    # parser instantiation
    soup = BeautifulSoup(content, "html.parser")

    # creating cache
    with open("cache.html", "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    print("soup scraped and cache set")


# whole dialogue
find_dialogue = soup.find("div", class_="dialogue")

with open("whole_dialogue.html", "w", encoding="utf-8") as file:
    file.write(find_dialogue.prettify())


# all conversations
conversations = find_dialogue.find_all("dl", recursive=False)

with open("conversations.html", "w", encoding="utf-8") as file:
    for conversation in conversations:
        file.write(conversation.prettify())


final_conversation_list = []

# structuring information
for conversation in conversations:
    # conversation struct: {scenario: x, dialogue: [line 1, line 2,..., line x]}
    conversation_formatted = {"scenario": None, "dialogue": []}

    # scenario
    conversation_formatted["scenario"] = (conversation.find("dt").string.strip() if conversation.find("dt") else None)

    # lines of dialogue
    lines = conversation.find_all("dd", recursive=False)

    for line in lines:
        # handling player options
        if line.find("span"): # ZZZ wiki uses spans in order to show the arrows that indicate player options
            
            children = list(line.children)
            char_response = None

            # player dialogue with responses. 5 as +1 for dl that holds character response + 1 for \n
            if len(children) == 5: 
                char_response = list(list(line.children)[3].dd.children)[-1].strip()
            
            #actual player option
            option = list(line.children)[2].strip()

            conversation_formatted["dialogue"][-1]["responses"].append({"prompt": option, "response": char_response})
            
        
        # handling character's dialogue 
        else:
            # {character: x, prompt: y, responses?: [{prompt: z, response: m}, {prompt: z, response: m}]}
            character = line.b.string.strip().strip(":")
            prompt = list(line.children)[-1].strip()
            conversation_formatted["dialogue"].append({"character": character, "prompt": prompt, "responses": []})

    final_conversation_list.append(conversation_formatted)


with open("conversations.json", "w", encoding="utf-8") as file:
    json.dump(final_conversation_list, file, indent=4)
        




