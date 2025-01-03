# -*- coding: utf-8 -*-
"""
Script to generate a book with dark fantasy themes inspired by various works,
now with an AI-powered review process, using imperative prompts and dynamic keyword extraction.
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
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import yaml
import logging
import random
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# -------------- CONFIGURATION FUNCTIONS  -------------- #
def load_restricted_words():
    """Load restricted words from file."""
    try:
        with open('restricted_words.txt', 'r', encoding='utf-8') as f:
            return [word.strip() for word in f.readlines() if word.strip()]
    except FileNotFoundError:
        logging.warning("restricted_words.txt not found. Using default restricted words.")
        return ["very", "really", "just", "quite", "suddenly", "basically", "actually", "literally"]

def load_config():
    """Load and validate configuration, including API key from environment."""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("config.yaml not found.")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing config.yaml: {e}")
        raise

    config['api_key'] = os.environ.get('GOOGLE_API_KEY')
    if not config['api_key']:
        raise ValueError("La variable de entorno GOOGLE_API_KEY no está configurada.")

    # Set default model parameters if not present
    default_params = {
        "model_parameters": {
            "character_generation": {
                "temperature": 1.5,
                "top_p": 0.95,
                "max_output_tokens": 1024
            },
            "creative": {
                "temperature": 0.9,
                "top_p": 0.95,
                "max_output_tokens": 2048
            },
            "review": {
                "temperature": 0.7,
                "top_p": 0.8,
                "max_output_tokens": 1024
            }
        }
    }
    
    # Merge with defaults
    if "model_parameters" not in config:
        config["model_parameters"] = default_params["model_parameters"]
    
    # Load restricted words from file
    config["restricted_words"] = load_restricted_words()
    
    return config

def load_prompt_template(template_path):
    """Loads a prompt template from a text file."""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Prompt template not found: {template_path}")
        raise

def extract_keywords(model, book_title, config):
    """
    Extracts keywords from a book title using the Gemini API.
    """
    prompt = f"""
    EXTRACT the key themes and concepts from the following book title: "{book_title}".
    OUTPUT a list of keywords separated by commas.
    """
    response = make_model_call(model, prompt, get_generation_config(config, "creative"), config['safety_settings'])
    if not response:
         return []
    keywords = [keyword.strip() for keyword in response.split(",")]
    return keywords

def create_dynamic_filename(book_title):
    """
    Generates a dynamic filename based on the book title and current timestamp.
    """
    sanitized_title = "".join(
        c for c in book_title if c.isalnum() or c in (' ', '.', '-', '_')).rstrip()
    sanitized_title = sanitized_title.replace(" ", "_").lower()
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{sanitized_title}_book_{timestamp}"
    return pdf_filename

# -------------- API FUNCTIONS  -------------- #

def get_generation_config(config, model_type, additional_params=None):
  """Helper function to generate a GenerationConfig object."""
  model_params = config.get("model_parameters", {}).get(model_type, {})
  if additional_params:
     model_params.update(additional_params)
  return genai.GenerationConfig(**model_params)


def make_model_call(model, prompt, generation_config, safety_settings, base_delay=10, max_delay=120, retries=6):
    """Centralized function to make LLM API calls with exponential backoff."""
    
    full_text = ""
    for i in range(retries):
      try:
        result = model.generate_content(
                prompt,
                generation_config=generation_config,
                 safety_settings=safety_settings
        )
        full_text = result.text
        time.sleep(1)
        return full_text
      except Exception as e:
           logging.error(f"Error generating content (attempt {i+1}/{retries}): {e}")
           if "429" in str(e):
                delay = min(base_delay * (2 ** i), max_delay)
                logging.warning(f"Rate limit hit. Waiting {delay} seconds before retrying...")
                time.sleep(delay)
           elif i < retries - 1:
                time.sleep(60)
           else:
                logging.error("Failed to generate content after multiple retries.")
                return None
    return full_text

def generate_outline(model, config, keywords_string, safety_settings):
    """Generates the book outline respecting the num_chapters and num_subchapters from config.yaml."""
    
    prompt_template = load_prompt_template('prompt_chapters.txt')
    
    # Get the exact values from config
    num_chapters = config.get('num_chapters', 1)  # Default to 1 if not specified
    num_subchapters = config.get('num_subchapters', 2)  # Default to 2 if not specified
    book_title = config.get('book_title', 'Untitled')
    
    # Modify the prompt to explicitly request the exact number of chapters and subchapters
    prompt = f"""
    GENERATE a JSON structure for a book outline with EXACTLY {num_chapters} chapter(s) and EXACTLY {num_subchapters} subchapter(s) per chapter.
    The book title is: "{book_title}"
    Theme keywords: {keywords_string}
    
    The JSON MUST follow this EXACT structure:
    {{
        "chapters": [
            {{
                "chapter_title": "Chapter Title Here",
                "subchapters": [
                    {{
                        "subchapter_title": "Subchapter Title 1"
                    }},
                    {{
                        "subchapter_title": "Subchapter Title 2"
                    }}
                ]
            }}
        ]
    }}
    
    ENSURE:
    - Exactly {num_chapters} chapter(s)
    - Exactly {num_subchapters} subchapter(s) per chapter
    - All titles are relevant to the theme keywords
    - JSON format is strictly followed
    
    RESPOND ONLY with the JSON structure, no additional text.
    """
    
    try:
        result = make_model_call(model, prompt, get_generation_config(config, "creative"), safety_settings)
        
        if not result:
            logging.error("No outline data received")
            return None
            
        # Clean up the response
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:]
        if result.endswith("```"):
            result = result[:-3]
        
        # Parse and validate JSON
        try:
            chapter_titles = json.loads(result.strip())
            
            # Validate structure
            if not isinstance(chapter_titles, dict) or "chapters" not in chapter_titles:
                logging.error("Invalid outline structure: missing 'chapters' key")
                return None
                
            # Validate chapter count
            if len(chapter_titles["chapters"]) != num_chapters:
                logging.error(f"Invalid number of chapters. Expected {num_chapters}, got {len(chapter_titles['chapters'])}")
                return None
                
            # Validate each chapter
            for chapter in chapter_titles["chapters"]:
                if not isinstance(chapter, dict) or "chapter_title" not in chapter:
                    logging.error("Invalid chapter structure: missing 'chapter_title'")
                    return None
                    
                if "subchapters" not in chapter:
                    logging.error("Invalid chapter structure: missing 'subchapters'")
                    return None
                    
                # Validate subchapter count
                if len(chapter["subchapters"]) != num_subchapters:
                    logging.error(f"Invalid number of subchapters. Expected {num_subchapters}, got {len(chapter['subchapters'])}")
                    return None
                    
                # Validate each subchapter
                for subchapter in chapter["subchapters"]:
                    if not isinstance(subchapter, dict) or "subchapter_title" not in subchapter:
                        logging.error("Invalid subchapter structure: missing 'subchapter_title'")
                        return None
            
            return chapter_titles
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse outline JSON: {e}")
            logging.debug(f"Raw response: {result}")
            return None
            
    except Exception as e:
        logging.error(f"Error generating outline: {e}")
        return None
    
def generate_character_profiles(model, config, character_essences, keywords_string, safety_settings):
    """Generates detailed character profiles based on the character essences."""
    logging.debug("Generating character profiles...")
    prompt_template = load_prompt_template('prompt_character_development.txt')
    prompt = prompt_template.format(
        book_title=config['book_title'],
        character_essences=json.dumps(character_essences),
        keywords_string=keywords_string
    )
    

    result = make_model_call(model, prompt, get_generation_config(config, "character_generation"), safety_settings)

    logging.debug(f"Character Profiles Response: {result}")
    return result

def generate_world_elements_descriptions(model, config, keywords_string, safety_settings):
    """Generates descriptions for key world elements."""
    logging.debug("Generating world elements descriptions...")
    prompt_template = load_prompt_template('prompt_world_elements.txt')
    prompt = prompt_template.format(
        book_title=config['book_title'],
        world_elements=config['world_elements'],
        keywords_string=keywords_string
    )

    result = make_model_call(model, prompt, get_generation_config(config, "creative"), safety_settings)

    logging.debug(f"World Elements Descriptions Response: {result}")
    return result

def generate_character_essence(model, config, used_names, keywords_string, safety_settings):
    """Generates character essences for a subchapter."""
    
    prompt_character_essence = f"""
        GENERATE a JSON dictionary representing character essences for a dark fantasy novel titled '{config['book_title']}'.
        The dictionary MUST contain a list of unpredictable character essences.
        Each character essence MUST have a unique 'name' and a 'description'.
        The dictionary MUST have the following structure:
        {{
          "character_essences": [
            {{
              "name": "Unique Name 1",
              "description": "Description of the character"
            }},
           {{
              "name": "Unique Name 2",
              "description": "Description of the character"
            }}
          ]
        }}

        The characters MUST have a intricate and complex tone, even paradoxical, making sure they are unique and not archetypical.
        DO NOT include any introductory or explanatory text. ONLY output the JSON dictionary.
    """
    
    
    result_names = make_model_call(model, prompt_character_essence, get_generation_config(config, "character_generation"), safety_settings)

    logging.debug(f"Raw character essence response: {result_names}")  # Log the raw response

    # --- FIX: Remove the ```json and ``` tags ---
    json_text = result_names
    if json_text.startswith("```json"):
        json_text = json_text[len("```json"):].strip()
    if json_text.endswith("```"):
        json_text = json_text[:-len("```")].strip()
    # --- End of Fix ---

    try:
        character_essences = json.loads(json_text)
    except (json.JSONDecodeError, TypeError) as e:
        logging.error(f"Error decoding JSON response for character essences: {e}. Raw response: {result_names}")
        with open("result_names.txt", "w", encoding="utf-8") as f:
           f.write(result_names)
        return [], []
    
    new_names = [essence["name"].strip() for essence in character_essences.get("character_essences", []) ]
    
    # Ensure name uniqueness
    unique_names = []
    for name in new_names:
        if name not in used_names:
           unique_names.append(name)
           used_names.append(name)

    if len(unique_names) < len(new_names):
        logging.warning("Some generated character names were duplicates and were excluded.")

    return character_essences, unique_names

def generate_and_refine_section(model, review_model, config, prompt, safety_settings, is_transition=False, model_parameters=None):
  """Generates, reviews, and refines a section of text iteratively."""
  if model_parameters is None:
    model_parameters = config["model_parameters"]["creative"]
  
  full_text = make_model_call(model, prompt, get_generation_config(config, "creative", model_parameters), safety_settings)

  if not full_text:
    return None
  
  full_text = perform_comprehensive_review(model, config, full_text, safety_settings, is_transition)
  
  return full_text

def generate_subchapter_content(model, review_model, config, chapter, chapter_index, subchapter, subchapter_index, used_names, character_profiles, keywords_string, safety_settings, world_descriptions, character_motivations, scene_openings, scene_endings):
    """Generates content for a single subchapter, with iterative review and refinement."""
    subchapter_title = subchapter.get("subchapter_title")
    if not subchapter_title:
        logging.error(f"Missing 'subchapter_title' in subchapter data. Skipping.")
        return None, None, used_names, ""  # Return empty strings for safety

    logging.debug(f"Starting Subchapter {subchapter_index + 1}: {subchapter_title}")


    # --- Generate, Review, and Refine Transition ---
    transition_text = generate_and_refine_section(model, review_model, config,
                                                  load_prompt_template('prompt_transition.txt').format(
                                                      subchapter_title=subchapter_title),
                                                  safety_settings, is_transition=True)



    # --- Generate Names and Essences (No change needed)---
    character_essences, new_names = generate_character_essence(model, config, used_names, keywords_string, safety_settings)

    # Avoid appending to `used_names` if there's no data
    if new_names:
      used_names.extend(new_names)


    # --- Generate, Review, and Refine Subchapter Content ---
    sections_text = generate_and_refine_section(model, review_model, config,
                                                load_prompt_template('prompt_sections.txt').format(
                                                    subchapter_title=subchapter_title,
                                                    book_title=config['book_title'],
                                                    chapter_index=chapter_index,
                                                    new_names=", ".join(new_names) if new_names else "",
                                                    character_profiles=character_profiles,
                                                    restricted_words=", ".join(config['restricted_words']),
                                                    keywords_string=keywords_string,
                                                    opening_method=random.choice(scene_openings) if scene_openings else "",
                                                    ending_method=random.choice(scene_endings) if scene_endings else "",
                                                    world_description=random.choice(world_descriptions) if world_descriptions else "",
                                                    character_motivation=random.choice(character_motivations) if character_motivations else "",
                                                ),
                                                safety_settings)
    
    #Crucial Check: Handle empty results robustly
    if sections_text is None and transition_text is None:
        logging.warning(f"No valid content generated for subchapter {subchapter_title}. Skipping.")
        return None, None, used_names, ""


    # --- Combine Transition and Content ---
    chapter_content = f"### {subchapter_title}\n\n"
    chapter_content += transition_text + "\n\n" if transition_text else ""
    chapter_content += sections_text + "\n\n" if sections_text else ""

    return transition_text, sections_text, used_names, chapter_content

def perform_comprehensive_review(model, config, text, safety_settings, is_transition):
    """Performs a comprehensive review of the text for tone, style, and vocabulary."""
    prompt_template = load_prompt_template('prompt_comprehensive_revision.txt')
    if is_transition:
        prompt = prompt_template.format(text=text, restricted_words=config['restricted_words'], is_transition="a transition")
    else:
        prompt = prompt_template.format(text=text, restricted_words=config['restricted_words'], is_transition="a section of the story")

    generation_config = get_generation_config(config, "review")
    result = make_model_call(model, prompt, generation_config, safety_settings)
    logging.debug(f"Comprehensive Review Feedback:\n{result}\n")
    return result

def perform_ai_review(review_model, config, subchapter_title, sections_text, safety_settings):
    logging.debug(f"Performing AI review for subchapter '{subchapter_title}'")
    prompt_template = load_prompt_template('prompt_ai_review.txt')
    prompt_revision = prompt_template.format(
        subchapter_title=subchapter_title,
        book_title=config.get('book_title', 'Unknown Title'),
        sections_text=sections_text
    )
    generation_config = get_generation_config(config, "review")
    result_revision = make_model_call(review_model, prompt_revision, generation_config, safety_settings)
    revision_text = result_revision
    logging.debug(f"AI Review Feedback:\n{revision_text}\n")
    return revision_text

def output_book(book_title, book_content_elements, book_content_text):
    """Outputs the generated book to PDF and TXT files."""
    doc_filename = f"{create_dynamic_filename(book_title)}.pdf"
    doc = SimpleDocTemplate(doc_filename, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    doc.build(book_content_elements)
    txt_filename = f"{create_dynamic_filename(book_title)}.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(book_content_text)
    print(f"Book content written to {doc_filename} and {txt_filename}")

def generate_final_chapter(model, config, keywords_string, safety_settings):
    """Generates the final chapter of the book."""
    logging.debug("Generating final chapter...")
    prompt_template = load_prompt_template('prompt_final_chapter.txt')
    prompt = prompt_template.format(
        book_title=config['book_title'],
        keywords_string=keywords_string
    )

    result = make_model_call(model, prompt, get_generation_config(config, "creative"), safety_settings)

    logging.debug(f"Final Chapter Response: {result}")
    return result

# Define data structures using TypedDict for type hinting and schema validation
class Subchapter(typing.TypedDict):
    subchapter_title: str

class Chapter(typing.TypedDict):
    chapter_title: str
    subchapters: list[Subchapter]

class BookOutline(typing.TypedDict):
    book_title: str
    chapters: list[Chapter]
def generate_dynamic_list(model, config, prompt_template_path, keywords_string, safety_settings):
    """Generates a dynamic list using the model and the given prompt template."""
    prompt_template = load_prompt_template(prompt_template_path)
    prompt = prompt_template.format(
        book_title=config['book_title'],
        keywords_string=keywords_string
    )

    result = make_model_call(model, prompt, get_generation_config(config, "creative"), safety_settings)
    logging.debug(f"Generated dynamic list from {prompt_template_path}: {result}")
    return [line.strip() for line in result.splitlines() if line.strip()]

def generate_final_scene(model, config, keywords_string, safety_settings):
    """Generates the final scene JSON object of the book."""
    logging.debug("Generating final scene...")
    prompt_template = load_prompt_template('prompt_final_scene.txt')
    prompt = prompt_template.format(
        book_title=config['book_title'],
        keywords_string=keywords_string
    )

    # MODIFICACIÓN AQUÍ: Eliminar la especificación de response_mime_type
    result_json = make_model_call(model, prompt, get_generation_config(config, "creative"), safety_settings)
    if result_json is None:
        logging.error("No response for final scene, check logs")
        return None

    logging.debug(f"Final Scene Response: {result_json}")
    return result_json # Ahora esperamos texto, no JSON

def add_final_scene_to_output(final_scene, book_content_text, book_content_elements, styles):
    """Adds the final scene (as raw text) to the PDF elements and text content."""

    if final_scene is None:
        logging.warning("No final scene generated.")
        return book_content_text, book_content_elements

    try:
        # Process the final scene data.  Crucially, handle potential errors
        final_scene_data = json.loads(final_scene)
        
        book_content_text += "\nFinal Scene:\n"
        book_content_elements.append(Paragraph("Final Scene", styles['Heading1']))
        
        for element in final_scene_data:
           # Check if element has necessary keys
           if "content" in element:
             book_content_elements.append(Paragraph(element['content'], styles['BodyText']))
             book_content_text += f"{element['content']}\n"
           else:
               logging.warning(f"Skipping element without 'content' in final scene: {element}")
    
    except (json.JSONDecodeError, TypeError) as e:
        logging.error(f"Error parsing or decoding final scene JSON: {e}. Raw data: {final_scene}")
        return book_content_text, book_content_elements  # Crucial: Don't crash on bad JSON
    
    return book_content_text, book_content_elements


def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    try:
        # --- Load Config from YAML ---
        config = load_config()

        # --- Load API ---
        genai.configure(api_key=config['api_key'])
        model = genai.GenerativeModel(config["model_name"])
        review_model = genai.GenerativeModel(config["review_model_name"])

        # --- Load Prompts ---
        safety_settings = {
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        config['safety_settings'] = safety_settings

        # --- Dynamic Keywords ---
        extracted_keywords = extract_keywords(model, config["book_title"], config)
        keywords_string = ", ".join(extracted_keywords)

        # --- Generate Dynamic Lists ---
        logging.debug("Generating Dynamic Lists")
        world_descriptions = generate_dynamic_list(model, config, "prompt_world_descriptions.txt", keywords_string, safety_settings)
        character_motivations = generate_dynamic_list(model, config, "prompt_character_motivations.txt", keywords_string, safety_settings)
        scene_openings = generate_dynamic_list(model, config, "prompt_scene_openings.txt", keywords_string, safety_settings)
        scene_endings = generate_dynamic_list(model, config, "prompt_scene_endings.txt", keywords_string, safety_settings)

        # --- Generate Outline ---
        chapter_titles = generate_outline(model, config, keywords_string, safety_settings)

        if not chapter_titles:
          logging.error("Failed to generate chapter titles. Exiting.")
          return

        used_names = []
        character_profiles = {}

        book_content_elements = []
        book_content_text = f"# {config['book_title']}\n\n"
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='FirstParagraph', parent=styles['Normal'], spaceBefore=6, spaceAfter=6))

        # --- Loop para generar Capítulos y Subcapítulos ---
        if chapter_titles and "chapters" in chapter_titles:
            for i, chapter in enumerate(chapter_titles["chapters"]):
                chapter_title = chapter["chapter_title"]
                logging.debug(f"Starting Chapter {i + 1}: {chapter_title}")

                # Add chapter title to PDF and text
                book_content_elements.append(Paragraph(f"Chapter {i + 1}: {chapter_title}", styles['Heading1']))
                book_content_elements.append(Spacer(1, 0.5 * inch))
                book_content_text += f"## Chapter {i + 1}: {chapter_title}\n\n"

                if "subchapters" in chapter:
                    for subchapter in chapter["subchapters"]:
                        # Generate and process subchapter content
                        transition_text, sections_text, used_names, chapter_content = generate_subchapter_content(
                            model, review_model, config, chapter, i, subchapter, len(chapter["subchapters"]), used_names,
                            character_profiles, keywords_string, safety_settings, world_descriptions,
                            character_motivations, scene_openings, scene_endings
                        )
                        if not chapter_content:  # Crucial check
                            logging.warning(f"Skipping empty subchapter content for Chapter {i + 1}, Subchapter {subchapter}.")
                            continue
                        
                        # Add content to both text and PDF
                        book_content_text += chapter_content
                        book_content_elements.append(Paragraph(subchapter.get("subchapter_title", ""), styles['Heading2']))
                        if transition_text:
                          book_content_elements.append(Paragraph(transition_text, styles['BodyText']))
                          book_content_elements.append(Spacer(1, 0.25 * inch))

                        sections = sections_text.split('\n\n')
                        for k, section in enumerate(sections):
                            # Conditional formatting for the first section within a subchapter
                            if k == 0:
                                book_content_elements.append(Paragraph(section, styles['FirstParagraph']))
                            else:
                                book_content_elements.append(Paragraph(section, styles['BodyText']))
                            if k < len(sections) - 1:
                                book_content_elements.append(Spacer(1, 6))  # Add more space if needed

                #Add chapter closing, this is important to correctly format the chapters
                else:
                    logging.error(f"No subchapters found for Chapter {i + 1}.")
                book_content_text += "---End of Chapter---\n\n"
            
            # Generate and add the final chapter and scene
            final_text = generate_final_chapter(model, config, keywords_string, safety_settings)
            book_content_text += f"{final_text}\n"
            book_content_elements.append(Paragraph(final_text, styles['BodyText']))


            final_scene = generate_final_scene(model, config, keywords_string, safety_settings)
            book_content_text, book_content_elements = add_final_scene_to_output(final_scene, book_content_text, book_content_elements, styles)


            output_book(config['book_title'], book_content_elements, book_content_text)

    except FileNotFoundError as e:
        logging.error(f"File not found: {e.filename}")
        print(f"Error: Could not find file: {e.filename}")
    except ValueError as e:
        logging.error(f"Value Error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")



if __name__ == "__main__":
    main()