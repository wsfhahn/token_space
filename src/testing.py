from openai import OpenAI

string = "The dominant sequence transduction models are based on complex recurrent or convolutional"

client = OpenAI(
    base_url="http://100.95.73.15:1234/v1",
    api_key="v1"
)

model = "llama-3.1-70b-base"

string += client.completions.create(
    model=model,
    prompt=string,
    max_tokens=20
).choices[0].text

print(string)