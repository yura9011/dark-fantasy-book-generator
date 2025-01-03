# -*- coding: utf-8 -*-
"""
Script to generate a book with dark fantasy themes inspired by various works,
now with an AI-powered review process, using imperative prompts.
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
# API Key se configura usando la variable de entorno
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=api_key)
modelName = "learnlm-1.5-pro-experimental"  # Model name for the AI
book_title = "Defense of the Ancients ( Dota2 ) Book of Shadows"  # Title of the book
num_chapters = 3  # Number of chapters in the book
num_subchapters = 3  # Number of subchapters per chapter
modelTemperature = 0.7  # Temperature for content generation (0.0-1.0, higher = more creative)
modelTopP = 0.95  # Top_p for content generation (0.0-1.0, controls diversity)
modelMaxOutputTokens = 8192  # Maximum number of tokens for AI output
reviewModelTemperature = 0.5  # Temperature for the AI review process
reviewModelMaxOutputTokens = 4096  # Maximum tokens for the AI review
# --- Restricted words ---
restricted_words = [ "shatter", "shattered", "shattered", "echo", "echoes","echoes","meticulous", "meticulously", "navigating", "complexities", "realm", "understanding", "dive in", "shall", "tailored", "towards", "underpins", "everchanging", "ever-evolving", "the world of", "not only", "alright", "embark", "Journey", "In today's digital age", "hey", "game changer", "designed to enhance", "it is advisable", "daunting", "in the realm of", "amongst", "unlock the secrets", "unveil the secrets", "and robust", "diving", "elevate", "unleash", "power", "cutting-edge", "rapidly", "expanding", "mastering", "excels", "harness", "imagine", "It's important to note", "Delve into", "Tapestry", "Bustling", "In summary", "Remember that", "Take a dive into", "Navigating", "Landscape", "Testament", "In the world of", "Realm", "Embark", "Analogies to being a conductor or to music", "Vibrant", "Metropolis", "Firstly", "Moreover", "Crucial", "To consider", "There are a few considerations", "Ensure", "Furthermore", "Fancy", "As a professional", "Therefore", "Additionally", "Specifically", "Generally", "Consequently", "Importantly", "nitty-gritty", "Thus", "Alternatively", "Notably", "As well as", "Weave", "Despite", "Essentially", "While", "Also", "Even though", "Because", "In contrast", "Although", "In order to", "Due to", "Even if", "Arguably", "On the other hand", "It's worth noting that", "To summarize", "Ultimately", "To put it simply", "Promptly", "Dive into", "In today's digital era", "Reverberate", "Enhance", "Emphasize", "Revolutionize", "Foster", "Remnant", "Subsequently", "Nestled", "Game changer", "Labyrinth", "Enigma", "Whispering", "Sights unseen", "Sounds unheard", "Indelible", "My friend", "Buzz", "In conclusion", "gaze", "voice", "grim", "dark", "shadow/shadows", "light", "eyes", "seemed", "like", "felt", "though", "around", "suddenly", "still", "just", "even", "now", "back", "almost", "upon", "within", "beneath", "against", "amidst", "grimace", "However", "Indeed", "Nevertheless", "Particularly", "Significantly", "Remarkably", "Potentially", "Accordingly", "Conversely", "besides", "as a result", "because of this", "for this reason", "regardless", "notwithstanding", "whereas", "similarly", "likewise", "comparatively", "meanwhile", "afterward", "previously", "basically", "fundamentally", "primarily", "crucially", "especially", "absolutely", "definitely", "clearly", "obviously", "if", "unless", "provided that", "although", "despite", "secondly", "thirdly", "finally", "initially", "certainly", "undoubtedly", "presumably", "possibly", "likely", "typically", "usually", "namely", "abruptly", "instantaneously", "unexpectedly", "in addition to", "as well as", "coupled with", "not only that", "on top of that", "on the contrary", "instead", "while", "despite this", "in spite of", "yet", "still", "hence", "thus", "in the event that", "as long as", "on the condition that", "in particular", "above all", "next", "at the same time", "for example", "for instance", "such as", "that is", "in other words", "to illustrate", "to demonstrate", "to sum up", "in short", "overall", "in essence", "absolutely", "certainly", "clearly", "obviously", "undoubtedly", "particularly", "significantly", "vitally", "above all", "mainly", "precisely", "exactly", "literally", "strictly", "unequivocally", "explicitly", "comprehensively", "accurately", "solely", "highly", "greatly", "deeply", "thoroughly", "fully", "completely", "extremely", "intensely", "exceptionally", "utterly", "considerably", "more importantly", "most significantly", "it is crucial that", "it is essential that", "of utmost importance", "to a great extent", "to a large degree"]

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
review_model = genai.GenerativeModel(modelName)  # You can use a different model for review if desired

def create_dynamic_filename(book_title):
    """
    Generates a dynamic filename based on the book title and current timestamp.
    """
    sanitized_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '.', '-', '_')).rstrip()
    sanitized_title = sanitized_title.replace(" ", "_").lower()
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{sanitized_title}_book_{timestamp}"
    return pdf_filename

# --- First Call: Generate Chapter Titles ---
prompt_chapters = f"""
CREATE a JSON dictionary representing the outline for a dark fantasy book titled '{book_title}'.
The dictionary MUST contain EXACTLY {num_chapters} chapter(s).
Each chapter MUST contain EXACTLY {num_subchapters} subchapter(s).
The dictionary MUST have the following structure:
{{
  "book_title": "{book_title}",
  "chapters": [
    {{
      "chapter_title": "Title of Chapter 1",
      "subchapters": [
        {{"subchapter_title": "Title of Subchapter 1.1"}}
      ]
    }}
  ]
}}
GENERATE unique and evocative chapter titles suitable for dark fantasy.
FOR each chapter, GENERATE unique and evocative subchapter titles, maintaining the dark fantasy tone.
DO NOT include any introductory or explanatory text. ONLY output the JSON dictionary.
"""

print(f"DEBUG: Generating outline for book {book_title}")

result_chapters = model.generate_content(
    prompt_chapters,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=BookOutline,
        temperature=modelTemperature,
        top_p=modelTopP,
        max_output_tokens=modelMaxOutputTokens,
    ),
)

chapter_titles = result_chapters.candidates[0].content.parts[0].text
chapter_titles = eval(chapter_titles)

# --- Second Call & Beyond: Iteratively Generate Content with AI Review ---

book_content = ""
book_title = chapter_titles.get("book_title", book_title)

book_content_elements = []
book_content_text = ""

# --- PDF Setup with ReportLab ---
pdf_filename = f"{create_dynamic_filename(book_title)}.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                        rightMargin=inch, leftMargin=inch,
                        topMargin=inch, bottomMargin=inch)
styles = getSampleStyleSheet()

styles['Title'].fontSize = 28
styles['Title'].alignment = 1
styles['Title'].leading = 14
styles['Title'].spaceAfter = inch

styles['Heading1'].fontSize = 22
styles['Heading1'].spaceAfter = inch * 0.5

styles['Heading2'].fontSize = 16
styles['Heading2'].spaceAfter = inch * 0.25

styles.add(ParagraphStyle(name='FirstParagraph',
                          parent=styles['BodyText'],
                          firstLineIndent=0.5 * inch,
                          fontSize=11,
                          leading=14,
                          alignment=4))

styles['BodyText'].fontSize = 11
styles['BodyText'].leading = 14
styles['BodyText'].alignment = 4

# Add Title to PDF
book_content_elements.append(Paragraph(book_title, styles['Title']))
book_content_text += f"# {book_title}\n\n"

# --- Character Profiles ---
# Create a list of characters (or extract it from the prompt)
character_names = ["Lyra", "Kaelen", "Silas", "Theron", "Evelyn"]
character_profiles = {}  # Dictionary to store the profiles
for character_name in character_names:
    print(f"  DEBUG: Generating profile for character {character_name}")
    prompt_character_profile = f"""
    DESCRIBE the character {character_name} for the dark fantasy novel '{book_title}'.
    INCLUDE their physical description, personality traits, backstory, ambitions, fears, and relationships with other characters.
    ENSURE the character is believable and appropriate for the dark fantasy genre.
    DESCRIBE how the character might evolve throughout the story.
    """
    result_character = model.generate_content(
        prompt_character_profile,
        generation_config=genai.GenerationConfig(
            temperature=modelTemperature,
            top_p=modelTopP,
            max_output_tokens=modelMaxOutputTokens,
        ),
    )
    character_profiles[character_name] = result_character.text  # Save the profile in the dictionary
    print(f"  DEBUG: Profile of {character_name} created")

used_names = []  # List to store used names

# --- Loop para generar múltiples Capítulos y Subcapítulos ---
if chapter_titles and "chapters" in chapter_titles:
    for i, chapter in enumerate(chapter_titles["chapters"]):
        chapter_title = chapter["chapter_title"]
        book_content_text += f"## Chapter {i+1}: {chapter_title}\n\n"
        book_content_elements.append(Paragraph(f"Chapter {i+1}: {chapter_title}", styles['Heading1']))
        print(f"  DEBUG: Starting Chapter {i+1}: {chapter_title}")

        if "subchapters" in chapter:
            for j, subchapter in enumerate(chapter["subchapters"]):
                subchapter_title = subchapter["subchapter_title"]
                book_content_elements.append(Paragraph(subchapter_title, styles['Heading2']))
                print(f"    DEBUG: Starting Subchapter {j+1}: {subchapter_title}")

                # --- Generar Transición ---
                print(f"    DEBUG: Generating transition for subchapter '{subchapter_title}'")
                prompt_transition = f"""
                        CREATE a transition scene that seamlessly connects the previous subchapter to the new subchapter titled '{subchapter_title}'.
                        INCLUDE vivid sensory language.
                        CONNECT the current scene to the previous one.
                        SHOW key characters actions.
                        SET the mood.
                        USE unique descriptions, similes and metaphors.
                        BEGIN with a character action, a dialogue or an unusual description of the environment.
                        DO NOT use similar sensory details or settings that have already been used in the story.
                        """
                result_transition = model.generate_content(
                    prompt_transition,
                    generation_config=genai.GenerationConfig(
                        temperature=modelTemperature,
                        top_p=modelTopP,
                        max_output_tokens=modelMaxOutputTokens,
                    ),
                )
                transition_text = result_transition.text

                # --- Generate Names ---
                print(f"    DEBUG: Generating names for subchapter '{subchapter_title}'")
                prompt_generate_names = f"""
                    GENERATE a list of 5 unique, evocative names suitable for characters in a dark fantasy novel titled '{book_title}'.
                    The story is set in a world scarred by a cataclysm, with twisted technology and corrupted magic.

                    Consider the following character essences for this subchapter:
                    1. The Haunted Warrior: Scared, betrayed, seeking redemption through violence.
                    2. The Forbidden Scholar: Obsessed with dangerous knowledge.
                    3. The Shadowed Rogue: Loyalties tested by darkness.
                    4. The Corrupted Mystic: Wields dangerous, tainted magic.
                    5. The Hidden Deceiver: Conceals their true nature and motives.

                    The names MUST be unique and reflect the dark fantasy tone.
                    DO NOT use names already used in the story: {used_names}.
                    ONLY output the list of 5 names, separated by commas. DO NOT include any descriptions or explanations.
                """
                result_names = model.generate_content(
                    prompt_generate_names,
                    generation_config=genai.GenerationConfig(
                        temperature=modelTemperature,
                        top_p=modelTopP,
                        max_output_tokens=100,  # Adjust according to the number of names
                    ),
                )
                new_names = result_names.text.split(",")
                new_names = [name.strip() for name in new_names]  # Clean up spaces
                used_names.extend(new_names)  # Add new names to the list of used names

                # --- Modified Prompt for Content Generation ---
                prompt_sections = f"""
                        WRITE a detailed and captivating subchapter titled '{subchapter_title}' for the dark fantasy book '{book_title}', part of Chapter {i+1}.

                        The story MUST be set in a grim, dystopian world inspired by Berserk, Attack on Titan, and Fullmetal Alchemist.
                        INTEGRATE elements of twisted technology and magic, drawing inspiration from Akira, Serial Experiments Lain, and Ogre Battle.
                        ADVANCE the main plot, focusing on a group of characters fighting against a powerful, oppressive force.

                        USE the following character profiles as a foundation: {character_profiles}
                        ASSIGN these names to the characters within this subchapter: {', '.join(new_names)}.
                        FOCUS on their motivations, fears, and relationships, and show different points of view.

                        ADHERE to a dark and evocative tone.

                        Use a DIFFERENT beginning for each scene, using a different approach. Some scenes must start with character's thoughts, some with an action scene, and some with an unusual or specific description of the environment.

                        SHOW, don't tell: Convey emotions through actions, body language, and internal thoughts.
                        USE vivid sensory details to immerse the reader. DO NOT overuse previous sensory details.
                        RESTRICT vocabulary: Use the following words no more than twice: {restricted_words}.
                        USE a different kind of ending for each scene. Some endings should use a character's final thoughts, some a reveal of an important element, and others a moment that creates tension for the next scene.
                        DO NOT repeat any phrases or patterns from previous subchapters.
                        AVOID cliches.

                        ONLY output the content of the subchapter. DO NOT include the subchapter title, chapter title, or book title. DO NOT use any markdown.
                        """
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
                        sections_text = result_sections.text

                        # --- Tone Review ---
                        print(f"    DEBUG: Reviewing Tone for subchapter '{subchapter_title}'")
                        prompt_tone_review = f"""
                            ANALYZE the following text for tone inconsistencies.
                            Text: '{sections_text}'
                                IDENTIFY passages inconsistent with the dark fantasy tone.

                                FOR EACH identified inconsistency:
                                    SUGGEST specific REWRITES that:
                                        MAINTAIN the dark fantasy tone.
                                        USE unique and descriptive language.
                                        AVOID repeated phrases and patterns used previously.
                                        USE vivid imagery and sensory details, different from the ones used before.
                                        CREATE a feeling of dread, tension and oppresion.

                            The response MUST be an improved rewritten version of the text with ALL the suggested changes applied.
                            """
                        result_tone_review = model.generate_content(
                            prompt_tone_review,
                            generation_config=genai.GenerationConfig(
                                temperature=reviewModelTemperature,
                                top_p=modelTopP,
                                max_output_tokens=reviewModelMaxOutputTokens,
                            ),
                        )
                        tone_review_text = result_tone_review.text
                        print(f"    DEBUG: Tone Review Feedback:\n{tone_review_text}\n")

                        # --- Show, Don't Tell Review ---
                        print(f"    DEBUG: Reviewing 'Show, Don't Tell' for subchapter '{subchapter_title}'")
                        prompt_show_dont_tell_review = f"""
                                ANALYZE the provided text for instances where emotions or sensations are stated directly, rather than being shown through evocative descriptions.
                                Text: '{sections_text}'

                                FOR EACH instance of 'telling':
                                    REWRITE the sentence using the following points:
                                        DO NOT tell but SHOW using descriptions of action, body language, internal thoughts, or sensory details.
                                        MUST create a visceral response on the reader
                                        MUST be an unique sentence using different phrasing from previous sentences

                                The response MUST be an improved rewritten version of the text with ALL the suggested changes applied.
                                """
                        result_show_dont_tell_review = model.generate_content(
                            prompt_show_dont_tell_review,
                            generation_config=genai.GenerationConfig(
                                temperature=reviewModelTemperature,
                                top_p=modelTopP,
                                max_output_tokens=reviewModelMaxOutputTokens,
                            ),
                        )
                        show_dont_tell_review_text = result_show_dont_tell_review.text
                        print(f"    DEBUG: Show, Don't Tell Review Feedback:\n{show_dont_tell_review_text}\n")

                        # --- Revisión de Vocabulario ---
                        print(f"    DEBUG: Refining vocabulary for subchapter '{subchapter_title}'")
                        prompt_vocabulary_revision = f"""
                            PROOFREAD and EDIT the provided text.
                            Text: {sections_text}
                                PAY close attention to:
                                    grammar, punctuation and spelling.
                                    plot coherence and character consistency.
                                    naturality of dialogue.
                                    pacing and suspense.
                                    the story's tone, ensuring it remains consistent.
                                REWRITE the text to:
                                    REDUCE the use of overused words: {restricted_words}.
                                    USE UNIQUE and EVOCATIVE vocabulary.
                                    USE more interesting and less common phrases.
                                The response MUST be an improved rewritten version of the text with ALL the suggested changes applied.
                                """
                        result_vocabulary_revision = model.generate_content(
                            prompt_vocabulary_revision,
                            generation_config=genai.GenerationConfig(
                                temperature=modelTemperature,
                                top_p=modelTopP,
                                max_output_tokens=modelMaxOutputTokens,
                            ),
                        )
                        vocabulary_review_text = result_vocabulary_revision.text
                        print(f"    DEBUG: Vocabulary Review Feedback:\n{vocabulary_review_text}\n")

                        # --- AI Review Process ---
                        print(f"    DEBUG: Performing AI review for subchapter '{subchapter_title}'")
                        prompt_revision = f"""
                                ACT as a dark fantasy novel editor.
                                REVIEW the following text for the subchapter titled '{subchapter_title}' from the book '{book_title}'.

                                ENSURE the text is coherent and maintains a dark fantasy tone similar to Berserk.
                                CHECK for the intensity of fights like in YuYu Hakusho.
                                VERIFY a dystopian atmosphere like Attack on Titan.
                                ANALYZE for psychological and technological elements akin to Akira and Serial Experiments Lain.
                                CONFIRM the moral complexity of Fullmetal Alchemist.
                                EVALUATE for strategic elements similar to Ogre Battle.
                                ENSURE the descriptions are unique and not repetitive.
                                ENSURE that the characters are believable and diverse.
                                ENSURE that there's variation on the tone.
                                PROVIDE constructive criticism regarding narrative, description, characters, and coherence.
                                POINT out any grammatical or syntax errors.

                                REWRITE the text to improve:
                                plot coherence.
                                description quality.
                                characters development.
                                overall coherence of the story.

                                The response MUST be an improved rewritten version of the text with ALL the suggested changes applied.
                                Text to review:
                                {sections_text}
                            """

                        result_revision = review_model.generate_content(  # Use the review model
                            prompt_revision,
                            generation_config=genai.GenerationConfig(
                                temperature=reviewModelTemperature,
                                top_p=modelTopP,
                                max_output_tokens=reviewModelMaxOutputTokens,
                            ),
                        )
                        revision_text = result_revision.text
                        print(f"    DEBUG: AI Review Feedback:\n{revision_text}\n")

                        # --- Edits to add the content to the book ---
                        book_content_text += f"### {subchapter_title}\n\n"
                        book_content_text += f"{transition_text}\n\n"
                        book_content_text += f"{sections_text}\n\n"

                        sections = sections_text.split('\n\n')

                        book_content_elements.append(Paragraph(transition_text, styles['BodyText']))
                        book_content_elements.append(Spacer(1, 0.25 * inch))

                        for k, section in enumerate(sections):
                            if k == 0:
                                book_content_elements.append(Paragraph(section, styles['FirstParagraph']))
                            else:
                                book_content_elements.append(Paragraph(section, styles['BodyText']))

                            if k < len(sections) - 1:
                                book_content_elements.append(Spacer(1, 6))

                        # Imprimir la retroalimentación de la revisión, NO añadirla al contenido del libro
                        print("\n--- Feedback de Revisión ---")
                        print(f"Retroalimentación de Tono:\n{tone_review_text}\n")
                        print(f"Retroalimentación de Show, Don't Tell:\n{show_dont_tell_review_text}\n")
                        print(f"Retroalimentación de Vocabulario:\n{vocabulary_review_text}\n")
                        print(f"Retroalimentación General de la IA:\n{revision_text}\n")
                        print("--- Fin del Feedback de Revisión ---\n")

                        break
                    except Exception as e:
                        print(f"    DEBUG: An error occurred during generation: {e}")
                        print("    DEBUG: Retrying in 5 seconds...")
                        time.sleep(5)

        else:
            print(f"Error: No subchapters found for Chapter {i+1}.")
else:
    print("Error: No chapters found in the generated outline.")

# --- Output the Book ---
doc.build(book_content_elements)
txt_filename = f"{create_dynamic_filename(book_title)}.txt"
with open(txt_filename, "w", encoding="utf-8") as f:
    f.write(book_content_text)

print(f"Book content written to {pdf_filename} and {txt_filename}")