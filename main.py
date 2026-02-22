from openai import OpenAI
import dotenv
import json
import requests
from prompt import SYSTEM_PROMPT
from extract import extractInfo

dotenv.load_dotenv()

client = OpenAI()


def getWeatherInfo(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    weatherRes = requests.get(url=url)

    return weatherRes.text


def getGithubInfo(username: str):
    url = f"https://api.github.com/users/{username}"
    githubInfo = requests.get(
        url=url, headers={
            "User-Agent": "MyApp/1.0",
            "Accept": "application/vnd.github+json", 'X-GitHub-Api-Version': '2022-11-28'})
    data = githubInfo.json()


    if githubInfo.status_code == 404:
        return "Github user doesn't exist"
    else:
        return extractInfo(json.dumps(data), username)


def main():
    tools = {
        'tool_weather_info': getWeatherInfo,
        'tool_github_info': getGithubInfo
    }

    query = input(
        "Enter name of a city to find weather or ask something about the github profile of an user\n")

    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT
    }, {
        "role": "user",
        "content": query
    }]

    while (True):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
        )

        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content})

        parsedContent = json.loads(response.choices[0].message.content)

        if (parsedContent["step"] == "START"):
            print('🏃‍♂️ ' + parsedContent["content"])
            continue
        elif (parsedContent["step"] == "THINK"):
            print('🧠 ' + parsedContent["content"])

            if (parsedContent["output"]):
                messages.append(
                    {"role": "assistant", "content": json.dumps({
                        "step": "END",
                        "content": parsedContent["output"]
                    })})
                continue
            continue
        elif (parsedContent["step"] == "TOOL"):
            print(
                '🛠️ ', f"Running {parsedContent["tool_name"]} for input: {parsedContent["input"]}")
            weatherOrGithubInfo = tools[parsedContent["tool_name"]](
                parsedContent["input"])

            messages.append(
                {"role": "assistant", "content": json.dumps({"step": "OBSERVE", "output": weatherOrGithubInfo})})
            continue
        elif (parsedContent["step"] == "END"):
            print('✅ ' + parsedContent['content'])
            break


main()
