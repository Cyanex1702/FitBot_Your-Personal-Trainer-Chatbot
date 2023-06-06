import os
import openai
import gradio
from youtube_search import YoutubeSearch
from gradio import components

openai.api_key = "Type Your Api Key Here"


start_sequence = "\nTrainer:"
restart_sequence = "\nClient: "

prompt = "The following is a conversation with a gym trainer. The trainer is knowledgeable, helpful, and dedicated to helping you reach your fitness goals.\n\nClient: Hi, I need some guidance on my workout routine.\nTrainer: "

def openai_create(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.2,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.2,
        presence_penalty=0.6,
        stop=[" Client:", " Trainer:"]
    )
    return response.choices[0].text


def chatgpt_clone(input, history, client_info):
    history = history or []
    s = list(sum(history, ()))
    s.append(input)
    inp = ' '.join(s)
    inp += "\nClient Info: " + client_info
    output = openai_create(inp)
    history.append((input, output))
    return history, history


def search_videos(query, max_results=5):
    try:
        # Perform a YouTube search
        results = YoutubeSearch(query, max_results=max_results).to_dict()

        # Retrieve the video links
        video_links = [f"https://www.youtube.com/watch?v={result['id']}" for result in results]

        return video_links
    except Exception as e:
        print("An error occurred:", str(e))
        return []


def get_video_links(query):
    video_links = search_videos(query)
    return "\n".join(video_links)


def chat_interface(message, client_info, video_query):
    if message.strip() == "" and video_query.strip() == "":
        # Return empty outputs if both queries are empty
        return "", ""

    chatbot_output = ""
    video_links = ""

    if message.strip() != "":
        response = openai_create(message)
        chatbot_output = response.split("Trainer:")[-1].strip()

    if video_query.strip() != "":
        video_links = get_video_links(video_query)

    return chatbot_output, video_links


example_prompts = [
    "What are some good exercises for weight loss?",
    "How many calories should I consume in a day?",
    "Can you recommend a workout routine for beginners?"
]
client_info_examples = [
    "I am 5 feet 9 inches, 20 years old, and weigh 95 kg",
    "I have a shoulder injury",
    "I am a male and a beginner"
]
video_query_examples = [
    "Chest exercises video",
    "Diet plan for bulking",
    "Phonk x Aggressive Music for Gym Exercises"
]

iface = gradio.Interface(
    fn=chat_interface,
    inputs=[
        components.Textbox(label="Talk With Fit", lines=5, placeholder="Enter your message"),
        components.Textbox(label="Client Info", placeholder="Enter your height, age, weight, etc For better Personalized results"),
        components.Textbox(label="Search for Video", placeholder="Want to look up a video that explains more?")
    ],
    outputs=[
        components.Textbox(label="Chatbot Response", lines=5),
        components.Textbox(label="Video Link", lines=5)
    ],
    title="FitBot - Your Personal Gym Trainer",
    theme="default",
    examples=[
        [example_prompt, client_info_example, video_query_example]
        for example_prompt, client_info_example, video_query_example in zip(
            example_prompts, client_info_examples, video_query_examples
        )
    ]
)
iface.launch(inline=False, share=True)
