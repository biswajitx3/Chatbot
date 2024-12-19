import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

# Define the prompt template
template = """\
For the following text, extract the following \
information:

sentiment: Is the customer happy with the product? 
Answer Positive if yes, Negative if \
not, Neutral if either of them, or Unknown if unknown.

delivery_days: How many days did it take \
for the product to arrive? If this \
information is not found, output No information about this.

price_perception: How does it feel the customer about the price? 
Answer Expensive if the customer feels the product is expensive, 
Cheap if the customer feels the product is cheap,
not, Neutral if either of them, or Unknown if unknown.

Format the output as bullet-points text with the \
following keys:
- Sentiment
- How long took it to deliver?
- How was the price perceived?

text: {review}
"""

# PromptTemplate variables definition
prompt = PromptTemplate(
    input_variables=["review"],
    template=template,
)

# LLM and key loading function
def load_LLM(openai_api_key):
    """Logic for loading the chain you want to use should go here."""
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    return llm

# Streamlit page configuration
st.set_page_config(page_title="Extract Key Information from Product Reviews")
st.header("Extract Key Information from Product Reviews")

# Intro instructions
st.markdown("Extract key information from a product review URL.")
st.markdown("""
    - Sentiment
    - How long took it to deliver?
    - How was its price perceived?
    """)

# Input OpenAI API Key
st.markdown("## Enter Your OpenAI API Key")

def get_openai_api_key():
    input_text = st.text_input(
        label="OpenAI API Key",  
        placeholder="Ex: sk-2twmA8tfCb8un4...", 
        key="openai_api_key_input", 
        type="password"
    )
    return input_text

openai_api_key = get_openai_api_key()

# Input URL
st.markdown("## Enter the Product Review URL")

def get_review_url():
    review_url = st.text_input(
        label="Product Review URL",
        label_visibility='collapsed',
        placeholder="Enter the URL of the product review...",
        key="review_url"
    )
    return review_url

review_url = get_review_url()

# Function to fetch review content from the URL
def fetch_review_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Modify this selector based on the website structure
        # Example: Get all <p> tags from the page
        review_content = " ".join([p.text for p in soup.find_all('p')])
        return review_content.strip()
    except Exception as e:
        return None

# Display the extracted review content
review_input = ""
if review_url:
    review_input = fetch_review_content(review_url)
    if review_input:
        st.markdown("### Extracted Review Content:")
        st.write(review_input)
    else:
        st.error("Could not extract review content from the URL. Please check the URL and try again.")
        st.stop()

# Limit review input length
if len(review_input.split(" ")) > 700:
    st.error("The extracted review is too long. Please provide a shorter review.")
    st.stop()

# Output key data extraction
st.markdown("### Key Data Extracted:")

if review_input:
    if not openai_api_key:
        st.warning('Please insert OpenAI API Key. \
            Instructions [here](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)', 
            icon="⚠️")
        st.stop()

    llm = load_LLM(openai_api_key=openai_api_key)

    prompt_with_review = prompt.format(
        review=review_input
    )

    key_data_extraction = llm(prompt_with_review)

    st.write(key_data_extraction)
