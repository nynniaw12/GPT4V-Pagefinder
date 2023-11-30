import base64
import requests

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def prompt(task, prev, info):
    ClickAction = '{ "action": "click", "element": <element_number> }'
    TypeAction = '{ "action": "type", "element": <element_number>, "text": "<text>" }'
    RememberInfoFromSite = '{ "action": "remember-info", "info": "<info>" }'
    Done = '{ "action": "done" }'

    prompt_template = f"""task: Find out how to {task}

type ClickAction = {ClickAction}
type TypeAction = {TypeAction}
type RememberInfoFromSite = {RememberInfoFromSite}
type Done = {Done}

## response format
{{
  briefExplanation: string,
  nextAction: ClickAction | TypeAction | RememberInfoFromSite | Done
}}

## response examples
{{
  "briefExplanation": "Today's doodle looks interesting, I'll click it",
  "nextAction": {{ "action": "click", "element": 9 }}
}}
{{
  "briefExplanation": "I'll type 'funny cat videos' into the search bar",
  "nextAction": {{ "action": "type", "element": 11, "text": "funny cat videos" }}
}}
{{
  "briefExplanation": "Today's doodle is about Henrietta Lacks, I'll remember that for our blog post",
  "nextAction": {{ "action": "remember-info", "info": "Today's doodle is about Henrietta Lacks" }}
}}
{{
  "briefExplanation": "A doodle is accessed after clicking on today’s doodle.",
  "nextAction": {{ "action": "done"}}
}}

## previous action
{prev}

## stored info
{info}

## instructions
# observe the screenshot, and think about the next action
# prioritize intuitive actions i.e. clicking on elements located above on the screen
# do not propose actions based on speculation
# done when user input is necessary
# output your response in a json markdown code block
"""
    return prompt_template


def vision_decide(api_key, image_path, task, prev = "", info = ""):
    base64_image = encode_image(image_path)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt(task, prev, info)
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "medium"
            }
            }
        ]
        }
    ],
    "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response



