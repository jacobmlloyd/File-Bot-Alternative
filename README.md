# Filebot Alternative
 
 A simple alternative to the paid Filebot application to rename movie and TV show files using TheMovieDB metadata. This application is not secure and stores your saved API credentials in a JSON file called config.json. Use at your own risk. Future support of this application is undetermined based on uses. We do not condone pirating movies - please only use for your own media. This application only makes API request to The Movie DB -- it does NOT send data to our servers (due to privacy reasons, but also because we don't care enough to setup a server to spy on people when there's 0 benefit to anyone for such a simple application?)
 
 ## Requirements
 
 * Python 3.7+
 * customtkinter (`pip install customtkinter`)
 * requests (`pip install requests`)
 
 ## Setup
 
 * Install dependencies:
   ```
   pip install -r requirements.txt
   ```
 * Run the application:
   ```
   python main.py
   ```
 
 ## Usage

 1. Run the application:
    ```bash
    python main.py
    ```
 2. In the **Configuration** panel (left):
    - Select **Platform** (currently only The MovieDB).
    - Enter your TMDB **API Key** (signup at https://www.themoviedb.org).
    - Click **Save** to persist.
 3. In the **Main** area:
    - Click **Browse** to select your media folder (movies/TV shows).
    - Click **Scan** to preview original vs. new filenames side by side.
    - Click **Go** to apply the renames while preserving folder structure.
