import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_KEY')

def summarize_text(input_text):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Summarize the following extracted content from a webpage into concise, well-organized notes. Focus on key points, important details, and main takeaways. Break down the information into logical sections with bullet points or headings where necessary. The summary should be easy to review as study notes or a quick reference guide. Please ensure that the summary is concise but covers all essential points clearly, removing unnecessary or repetitive details. Ignore the description of webpage and focus only on the content present in it." + input_text)
    print(response)
    return response.text

if __name__ == '__main__':
    pass