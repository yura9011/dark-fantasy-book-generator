# Dark Fantasy Book Generator

<!-- Introduction/Description -->
This project is a Python script that generates a book with dark fantasy themes, drawing inspiration from various works such as *Berserk*, *Yu Yu Hakusho*, *Attack on Titan*, *Akira*, *Serial Experiments Lain*, *Fullmetal Alchemist*, and the *Ogre Battle* series. It uses Google's Gemini AI model to generate the book outline and content, and ReportLab to output the generated text into a well-formatted PDF.

<!-- Key Features -->
## Key Features
*   **AI-Powered Generation:** Uses Google's Gemini AI model to generate chapter outlines and content.
*   **Multiple Influences:** Combines elements from various dark fantasy, dystopian, and cyberpunk works to create a unique narrative.
*   **PDF and TXT Output:** Produces a well-formatted PDF and a plain text version of the book.
*   **Customizable:** Easily adjustable parameters for book title, number of chapters, and AI model settings.
*   **Dynamic File Naming:**  Generates dynamic filenames based on the book title and timestamp to avoid overwriting files.
*   **Modular Structure:** Well-structured code that is easy to read and modify, ideal for collaboration and expansion.
*   **Both Script and Notebook formats:** Provides the tool as both a Python script and a Jupyter Notebook, allowing both experienced and beginner users to access the project

<!-- How to use -->
## How to Use

1.  **Prerequisites:**
    *   A Google Cloud Platform (GCP) project with access to the Gemini API.
    *   Python 3.6+ installed.

2.  **Setup:**
    *   Clone this repository:
      ```bash
      git clone https://github.com/yourusername/dark-fantasy-book-generator.git
      ```
    *   Navigate to the repository:
      ```bash
      cd dark-fantasy-book-generator
      ```
    * Install the required packages:
       ```bash
      pip install google-generativeai reportlab typing_extensions
      ```
3.  **Configuration:**
    *   Open the `book_generator.py` script (or the `.ipynb` notebook).
    *   Find the configuration section (marked with `CONFIUGRE THESE VALUES`).
    *   **Replace** the placeholder API key (`AIxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) with your Google Gemini API key.
    *   Adjust the parameters to your preferences:
        *   `modelName`: The Google Gemini model to use.
        *   `book_title`: The title of your book.
        *   `num_chapters`: The number of chapters.
        *   `num_subchapters`: The number of subchapters in each chapter.
        *   `modelTemperature`: Controls randomness of AI. Lower values (e.g., 0.0) = more deterministic. Higher values (e.g., 1.0) = more random.
        *   `modelTopP`: Controls diversity.
        *   `modelMaxOutputTokens`: Maximum number of tokens the model can generate.

4.  **Running the Script:**
    *   To run the script, navigate to the repo folder in a terminal and run:
        ```bash
        python book_generator.py
        ```
    *  To run the notebook open the `.ipynb` file and run the cells.
5.  **Output:**
    *   The script will generate two files in the same directory:
        *   A PDF file (`[book_title]_book_[timestamp].pdf`) containing the formatted book.
        *   A plain text file (`[book_title]_book_[timestamp].txt`) with the raw text of the book.

<!-- Customization -->
## Customization

You can customize the following in the script:
*   **Prompts:** The prompts for generating the book outline and content are at the start of the script. You can adjust these to guide the AI model to follow a specific style, tone and include your own ideas.
*   **Themes:** By changing the prompts and the `book_title`, you can generate a book about any topic, not just dark fantasy.
*   **Output Format:** You can modify the PDF formatting by editing the ReportLab code.
*   **AI Settings:** Experiment with `modelTemperature` and `modelTopP` to control the creativity and diversity of the AI-generated text.

<!-- Dependencies -->
## Dependencies
*   `google-generativeai`: For interacting with the Gemini AI model.
*   `typing-extensions`: For type hinting
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

This project is licensed under the [Your License] License. Feel free to use and modify this script for personal or educational purposes.
=======
# dark-fantasy-book-generator
This project is a Python script that generates a book with dark fantasy themes. It uses Google's Gemini AI model to generate the book outline and content, and ReportLab to output the generated text into a well-formatted PDF.
>>>>>>> 87de5e85378cecba48cea5e5852244c08c2e7e35
