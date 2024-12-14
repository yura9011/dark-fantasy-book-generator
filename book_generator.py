# -*- coding: utf-8 -*-
"""
Script to generate a book with dark fantasy themes inspired by various works.
"""
import google.generativeai as genai
import typing_extensions as typing
import json
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
import datetime
import os

# -------------- CONFIGURE THESE VALUES -------------- #

# !!! IMPORTANT: Replace with your Gemini API key !!!
genai.configure(api_key="XXXXXXXXXX")  # <-- CHANGE THIS WITH YOUR API KEY
modelName = "gemini-2.0-flash-exp"  # Model name for the AI
book_title = "The Song of Broken Shadows"  # Title of the book
num_chapters = 3  # Number of chapters in the book
num_subchapters = 4  # Number of subchapters per chapter
modelTemperature = 0.8  # Temperature for the AI model (0.0-1.0, higher = more creative)
modelTopP = 0.95  # Top_p for the AI model (0.0-1.0, controls diversity)
modelMaxOutputTokens = 8192  # Maximum number of tokens for AI output
# --------------  END OF CONFIGURATION  -------------- #


# Define data structures using TypedDict for type hinting and schema validation
class Subchapter(typing.TypedDict):
    subchapter_title: str

class Chapter(typing.TypedDict):
    chapter_title: str
    subchapters: list[Subchapter]

class BookOutline(typing.TypedDict):
    book_title: str
    chapters: list[Chapter]


model = genai.GenerativeModel(modelName)

def create_dynamic_filename(book_title):
    """
    Generates a dynamic filename based on the book title and current timestamp.
    """
    sanitized_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '.', '-', '_')).rstrip() # Sanitize title for filename use
    sanitized_title = sanitized_title.replace(" ", "_").lower() # Convert spaces to underscores and lowercase
    now = datetime.datetime.now() # Current timestamp
    timestamp = now.strftime("%Y%m%d_%H%M%S") # Format: YYYYMMDD_HHMMSS
    pdf_filename = f"{sanitized_title}_book_{timestamp}" # Create filename with title and timestamp
    return pdf_filename

# --- First Call: Generate Chapter Titles ---
# Prompt to generate the book outline (chapters and subchapters)
prompt_chapters = f"""
Generate {num_chapters} chapter titles and for each chapter title, {num_subchapters} sub-chapter titles for a dark fantasy story titled '{book_title}'.
The story should have a tone of dark fantasy like Berzerk, the supernatural fights of YuYu Hakusho, a distopian setting similar to Attack on Titan, the tech and psychological elements of Akira and Serial Experiments Lain, the moral complexity of Fullmetal Alchemist, and the strategical elements of Ogre Battle the March of the Black Queen. Be as creative as you can when generating these chapters and subchapters, but maintain an overall tone of dark fantasy.
"""

print(f"DEBUG: Generating outline for book {book_title}")

# Generate the outline from the model
result_chapters = model.generate_content(
    prompt_chapters,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",  # Specify the expected JSON format of the response
        response_schema=BookOutline, # Specify the expected schema of the response
        temperature=modelTemperature, # Use configured temperature for response
        top_p=modelTopP, # Use configured top_p for response
        max_output_tokens=modelMaxOutputTokens,  # Use configured max output tokens for response
    ),
)

chapter_titles = result_chapters.candidates[0].content.parts[0].text # Parse the JSON response
chapter_titles = eval(chapter_titles)

# --- Second Call & Beyond: Iteratively Generate Content ---

book_content = ""  # Initialize an empty string to store the book content
book_title = chapter_titles.get("book_title", book_title)  # Get the title from the response, use the configured title as fallback

book_content_elements = []  # Initialize an empty list to store the content as ReportLab elements
book_content_text = "" # Initialize an empty string to store the content as plaintext

# --- PDF Setup with ReportLab ---
pdf_filename = f"{create_dynamic_filename(book_title)}.pdf" # Generate the PDF filename
doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                        rightMargin=inch, leftMargin=inch,
                        topMargin=inch, bottomMargin=inch)  # Setup document with margins
styles = getSampleStyleSheet()  # Get predefined styles

# Customize existing styles instead of adding new ones with the same name
styles['Title'].fontSize = 28
styles['Title'].alignment = 1  # Center alignment
styles['Title'].leading = 14
styles['Title'].spaceAfter = inch

styles['Heading1'].fontSize = 22
styles['Heading1'].spaceAfter = inch * 0.5

styles['Heading2'].fontSize = 16
styles['Heading2'].spaceAfter = inch * 0.25

# Create a new style for the first paragraph
styles.add(ParagraphStyle(name='FirstParagraph',
                          parent=styles['BodyText'],
                          firstLineIndent=0.5 * inch,
                          fontSize=11,
                          leading=14,
                          alignment=4))

styles['BodyText'].fontSize = 11
styles['BodyText'].leading = 14
styles['BodyText'].alignment = 4  # Justified alignment

# Add Title to PDF
book_content_elements.append(Paragraph(book_title, styles['Title'])) #Add book title to the PDF using "Title" style
book_content_text += f"# {book_title}\n\n" # Add book title to the text file

# Loop through chapters
for chapter_index, chapter in enumerate(chapter_titles["chapters"]):
    chapter_title = chapter["chapter_title"]
    book_content_text += f"## Chapter {chapter_index + 1}: {chapter_title}\n\n"  # Append chapter title with level 2 header for text file
    book_content_elements.append(Paragraph(f"Chapter {chapter_index + 1}: {chapter_title}", styles['Heading1'])) # Add chapter title using "Heading1" style for PDF
    print(f"  DEBUG: Starting Chapter {chapter_index + 1}: {chapter_title}") # Debug print message

    # Loop through subchapters
    for subchapter in chapter["subchapters"]:
        subchapter_title = subchapter["subchapter_title"]
        book_content_elements.append(Paragraph(subchapter_title, styles['Heading2']))  # Add subchapter title using "Heading2" style for PDF
        book_content_text += f"### {subchapter_title}\n\n"  # Append subchapter title with level 3 header for text file
        print(f"    DEBUG: Starting Subchapter {subchapter_title}") # Debug print message

        # Prompt for the generation of the content of the subchapter
        prompt_sections = f"""
        Write the content for the subchapter titled '{subchapter_title}' in the chapter '{chapter_title}' of a dark fantasy story titled '{book_title}'. The story should have a tone of dark fantasy like Berzerk, the supernatural fights of YuYu Hakusho, a distopian setting similar to Attack on Titan, the tech and psychological elements of Akira and Serial Experiments Lain, the moral complexity of Fullmetal Alchemist, and the strategical elements of Ogre Battle the March of the Black Queen. Be as creative as you can, but be true to the plot, characters and world that you have already created. Only output the content, don't output the subchapter title, chapter title and book title. Do not use any markdowns. Make it as detailed as you can.
        """
        # Keep trying until content has been generated successfully
        while True:
            try:
                result_sections = model.generate_content(
                    prompt_sections,
                    generation_config=genai.GenerationConfig(
                        temperature=modelTemperature,
                        top_p=modelTopP,
                        max_output_tokens=modelMaxOutputTokens,
                    ),
                )
                sections_text = result_sections.text # Get text from the AI model's response
                sections = sections_text.split('\n\n') # Split text by double newlines into individual sections
                # Loop through each section and add it to the PDF as a new paragraph
                for i, section in enumerate(sections):
                    if i == 0:
                        book_content_elements.append(Paragraph(section, styles['FirstParagraph'])) # Add first paragraph with "FirstParagraph" style
                    else:
                        book_content_elements.append(Paragraph(section, styles['BodyText']))  # Add remaining paragraphs with "BodyText" style

                    if i < len(sections) - 1:
                        book_content_elements.append(Spacer(1, 6)) # Add a small space after each section except the last one

                book_content_text += f"{sections_text.strip()}\n\n" # Append content to the text file
                break # Exit the loop if content was successfully generated
            except Exception as e:
                print(f"    DEBUG: An error occurred during generation: {e}")
                print("    DEBUG: Retrying in 5 seconds...")
                time.sleep(5)  # Wait for 5 seconds before retrying

# --- Output the Book ---
doc.build(book_content_elements)  # Build PDF
with open(f"{create_dynamic_filename(book_title)}.txt", "w", encoding="utf-8") as f: # Create and open text file
    f.write(book_content_text) # Write the plain text book content to the text file

print(f"Book content written to {book_title}.txt") # Print message to the console