# Dark Fantasy Book Generator

<!-- Introduction/Description -->
This project is a Python script that generates a book with dark fantasy themes, drawing inspiration from various works such as *Berserk*, *Yu Yu Hakusho*, *Attack on Titan*, *Akira*, *Serial Experiments Lain*, *Fullmetal Alchemist*, and the *Ogre Battle* series. It uses Google's Gemini AI model to generate the book outline and content, and ReportLab to output the generated text into a well-formatted PDF. A graphical user interface (GUI) has been added to make configuring the project easier for all users.

<!-- Key Features -->
## Key Features

*   **AI-Powered Generation:** Uses Google's Gemini AI model to generate chapter outlines and content.
*   **Multiple Influences:** Combines elements from various dark fantasy, dystopian, and cyberpunk works to create a unique narrative.
*   **AI-Powered Review Process:** Implements a multi-stage review for the AI-generated text (tone, show don't tell, vocabulary, and general review).
*   **Dynamic Character Creation:** Generates dynamic character names and profiles for each chapter and subchapter.
*   **Dynamic Transitions:** Generates transitions between subchapters to create a better narrative flow.
*   **Vocabulary Refinement:** Restricts the use of specific words to improve the quality of the text.
*   **PDF and TXT Output:** Produces a well-formatted PDF and a plain text version of the book.
*   **Customizable:** Easily adjustable parameters for book title, number of chapters, AI model settings, and prompts.
*   **Dynamic File Naming:** Generates dynamic filenames based on the book title and timestamp to avoid overwriting files.
*   **Modular Structure:** Well-structured code that is easy to read and modify, ideal for collaboration and expansion.
*   **Graphical User Interface (GUI):** Provides a user-friendly GUI created with Tkinter to easily adjust settings and modify prompts.
*   **Both Script and Notebook formats:** Provides the tool as both a Python script and a Jupyter Notebook, allowing both experienced and beginner users to access the project.
*   **Temporary Prompt Editing:** Changes made to prompts in the UI are not saved unless the "Save Prompt" button is clicked, ensuring your core prompts are safe.
*   **Selective Configuration Saving:**  Saving configuration only affects the `config.yaml` file, leaving prompt files untouched.

<!-- How to use -->
## How to Use

1.  **Prerequisites:**
    *   A Google Cloud Platform (GCP) project with access to the Gemini API.
    *   Python 3.9+ installed.

2.  **Setup:**
    *   Clone this repository:

        ```bash
        git clone https://github.com/yourusername/dark-fantasy-book-generator.git
        ```
    *   Navigate to the repository:

        ```bash
        cd dark-fantasy-book-generator
        ```
    *   Install the required packages:

        ```bash
        pip install google-generativeai reportlab typing_extensions python-dotenv
        ```

3.  **Configuration:**
    *   Copy the example `.env.example` file to `.env` and set the `GOOGLE_API_KEY` environment variable with your Google Gemini API key.
    *   Use the `ui_module.py` script to configure the project.
4.  **Running the Script:**
    *   To launch the UI, navigate to the repo folder in a terminal and run:

        ```bash
        python ui_module.py
        ```
    *   Adjust parameters, edit prompts and generate a book from the UI.
    *   To run the notebook open the `.ipynb` file and run the cells.
5.  **Output:**
    *   The script will generate two files in the same directory:
        *   A PDF file (`[book_title]_book_[timestamp].pdf`) containing the formatted book.
        *   A plain text file (`[book_title]_book_[timestamp].txt`) with the raw text of the book.

<!-- Customization -->
## Customization

You can customize the following in the script:

*   **Prompts:** The prompts for generating the book outline, content, transitions, character names, and character profiles are stored in `.txt` files. You can adjust these to guide the AI model to follow a specific style, tone, and include your own ideas. You can modify these through the UI.
*   **Themes:** By changing the prompts and the `book_title`, you can generate a book about any topic, not just dark fantasy.
*   **Output Format:** You can modify the PDF formatting by editing the ReportLab code.
*   **AI Settings:** Experiment with `modelTemperature`, `reviewModelTemperature`, and `modelTopP` to control the creativity and diversity of the AI-generated text and the tone and style of the review process.
*   **Restricted Words:** You can modify or add new words to the `restricted_words` list (located in `restricted_words.txt`) to fine-tune the tone and style of the generated content.

<!-- Dependencies -->
## Dependencies

*   `google-generativeai`: For interacting with the Gemini AI model.
*   `typing-extensions`: For type hinting.
*   `python-dotenv`: For handling environment variables.
*   `reportlab`: For generating the PDF output.

<!-- Contributing -->
## Contributing

If you want to contribute to this project, you can:

*   Open a Pull Request with your changes.
*   Open Issues in the Issues tab for bug reports or feature requests.

<!-- Acknowledgments and Credits -->
## Acknowledgments

*   This project was created by [Your Name] based on ideas and help from a large language model.
*   Thanks to the Google AI team for making the Gemini models available.

<!-- License -->
## License

This project is licensed under the MIT License. Feel free to use and modify this script for personal or educational purposes.

## Detailed Changelog (Old vs New Version)

**This section highlights the key changes between the old and new versions of the script.**

*   **API Key Handling:**
    *   **Old Version:** The API key was hardcoded directly in the script.
    *   **New Version:** The API key is now retrieved from the `GOOGLE_API_KEY` environment variable, improving security.
*   **AI-Powered Review Process:**
    *   **Old Version:** The script generated text content without any review.
    *   **New Version:** Implements a comprehensive review process with:
        *   **Tone Review:** Evaluates and refines the text for consistency with the dark fantasy tone.
        *   **"Show, Don't Tell" Review:** Identifies and rewrites sentences that state emotions directly instead of showing them through descriptions.
        *   **Vocabulary Review:** Restricts usage of words in the `restricted_words` list, enhancing the narrative style.
        *   **General AI Review:** A final review using another AI model to improve consistency, narrative, descriptions and characters.
*   **Character Names and Profiles:**
    *   **Old Version:** No character creation or management.
    *   **New Version:** Implements dynamic creation of character profiles and names for each subchapters, using these to enrich the story.
*   **Transitions:**
    *   **Old Version:** No scene transitions.
    *   **New Version:** Implements generation of transitions to connect the previous and current subchapters.
*   **Prompts:**
    *   **Old Version:**  Simple prompts for generating content.
    *   **New Version:**  New prompts for transitions, names, profiles, tone, vocabulary, show don't tell and general reviews were added, allowing for much more customization.
*   **Error Handling:**
    *   **Old Version:** Basic error handling.
    *   **New Version:** Try/except blocks have been added to make the script more robust when receiving API responses.
*   **Configuration:**
    *   **Old Version:** Simple hardcoded configuration variables.
    *   **New Version:** New variables for the review model `reviewModelTemperature`, `reviewModelMaxOutputTokens` and for the `restricted_words` list were added.
*   **Graphical User Interface (GUI):**
    *   **Old Version:** No UI.
    *   **New Version:** Added a full functional UI with Tkinter, allowing for all customization options available in the script.
    *  **Temporary Prompts:** The changes made to the prompts are not saved unless the 'Save Prompt' button is clicked, keeping the original prompts intact.
    *  **Configuration Saving:** Saving the configuration only saves the parameters to the `config.yaml`, keeping all prompt files untouched.
*  **Modular Structure**
   *   **Old Version:**  Monolithic script.
   *   **New Version:** The code has been separated in a main script `book_generatorv3.py` and the `ui_module.py`, making the code cleaner, easier to debug and maintain and ideal for collaboration.