#!/usr/bin/env python3
"""
CustomTkinter GUI application to rename movie and TV files using TheMovieDB metadata.
"""
import json
import os
from typing import List, Optional, Tuple

from tkinter import END, filedialog, messagebox
import customtkinter as ct

from parser import parse_movie, parse_tv
from tmdb_client import TMDBClient


class App(ct.CTk):
    provider: str
    api_key: str
    file_preview_list: List[Tuple[str, str]]
    folder_preview_list: List[Tuple[str, str]]

    def __init__(self, client: Optional[TMDBClient] = None) -> None:
        """Initialize the application, load configuration, and set up the UI."""
        super().__init__()
        self.title('Filebot Alternative')
        # initial window size and minimum dimensions
        self.geometry('1000x700')
        self.minsize(1000, 700)
        ct.set_appearance_mode('System')
        ct.set_default_color_theme('blue')
        # Configuration persistence
        self.config_file: str = os.path.join(os.getcwd(), 'config.json')
        self.load_config()
        # Allow dependency injection of TMDB client for testing
        if client is not None:
            self.client = client
        else:
            # Instantiate client using configured API key
            self.client = TMDBClient(self.api_key)
        # List of tuples (original_path, new_path) for preview and renaming
        self.preview_list: List[Tuple[str, str]] = []
        # Prepare preview lists for files and folders
        self.file_preview_list: List[Tuple[str, str]] = []
        self.folder_preview_list: List[Tuple[str, str]] = []
        self.create_widgets()

    def load_config(self) -> None:
        """
        Load the provider and API key from the JSON config file.
        Initializes self.provider and self.api_key.
        """
        try:
            with open(self.config_file, 'r') as f:
                cfg = json.load(f)
            self.provider = cfg.get('provider', 'TMDB')
            self.api_key = cfg.get('api_key', '')
        except Exception:
            self.provider = 'TMDB'
            self.api_key = ''

    def save_config(self) -> None:
        """
        Save the selected provider and API key to the JSON config file.
        Updates self.client based on the new API key.
        """
        self.provider = self.provider_menu.get()
        self.api_key = self.api_key_entry.get().strip()
        cfg = {'provider': self.provider, 'api_key': self.api_key}
        try:
            with open(self.config_file, 'w') as f:
                json.dump(cfg, f, indent=4)
            # reinitialize client with new API key
            if self.provider == 'TMDB':
                self.client = TMDBClient(self.api_key)
            messagebox.showinfo('Config', 'Configuration saved')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to save config: {e}')

    def on_provider_change(self, value: str) -> None:
        """
        Handle changes in provider selection by updating the provider attribute.
        """
        self.provider = value

    def create_widgets(self) -> None:
        """
        Set up the user interface: configuration panel, directory selectors, preview tables, and action buttons.
        """
        # Configuration panel on the left
        cfg_frame = ct.CTkFrame(self, width=200)
        cfg_frame.pack(side='left', fill='y', padx=(10,0), pady=10)
        ct.CTkLabel(cfg_frame, text='Configuration', font=ct.CTkFont(size=16, weight='bold')).pack(pady=(0,10))
        # Platform selection
        ct.CTkLabel(cfg_frame, text='Platform:', anchor='w').pack(fill='x', padx=10)
        self.provider_menu = ct.CTkOptionMenu(cfg_frame, values=['TMDB'], command=self.on_provider_change)
        self.provider_menu.set(self.provider)
        self.provider_menu.pack(fill='x', padx=10, pady=(0,10))
        # API key entry
        ct.CTkLabel(cfg_frame, text='API Key:', anchor='w').pack(fill='x', padx=10)
        self.api_key_entry = ct.CTkEntry(cfg_frame, width=180, show='*')
        if hasattr(self, 'api_key') and self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        self.api_key_entry.pack(fill='x', padx=10, pady=(0,10))
        # Save button
        ct.CTkButton(cfg_frame, text='Save', command=self.save_config).pack(pady=(0,20), padx=10)

        # Main area
        main_frame = ct.CTkFrame(self)
        main_frame.pack(side='left', fill='both', expand=True, padx=(10,10), pady=10)
        # Directory selection
        dir_frame = ct.CTkFrame(main_frame)
        dir_frame.pack(fill='x', padx=10, pady=(0,10))
        self.dir_entry = ct.CTkEntry(dir_frame, width=500)
        self.dir_entry.pack(side='left', padx=(0,5))
        ct.CTkButton(dir_frame, text='Browse', width=80, command=self.browse_folder).pack(side='left', padx=(0,5))
        ct.CTkButton(dir_frame, text='Scan', width=80, command=self.scan_folder).pack(side='left')

        # Preview panels: two tables side by side
        preview_frame = ct.CTkFrame(main_frame)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        # Headers
        hdr_frame = ct.CTkFrame(preview_frame)
        hdr_frame.pack(fill='x')
        ct.CTkLabel(hdr_frame, text='Original', anchor='w').pack(side='left', padx=(5,10))
        ct.CTkLabel(hdr_frame, text='New', anchor='w').pack(side='left', padx=(5,10))
        # Content boxes
        content_frame = ct.CTkFrame(preview_frame)
        content_frame.pack(fill='both', expand=True)
        self.orig_text = ct.CTkTextbox(content_frame, width=360, height=400)
        self.orig_text.pack(side='left', padx=(5,5), pady=5, fill='both', expand=True)
        self.new_text = ct.CTkTextbox(content_frame, width=360, height=400)
        self.new_text.pack(side='left', padx=(5,5), pady=5, fill='both', expand=True)
        # Rename button
        ct.CTkButton(main_frame, text='Rename', width=80, command=self.rename_files).pack(pady=(0,10))

    def browse_folder(self) -> None:
        """
        Open a directory selection dialog and populate the folder entry.
        """
        folder = filedialog.askdirectory()
        if folder:
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, folder)

    def scan_folder(self) -> None:
        """
        Scan the selected directory for media files, prepare file and folder renames,
        and display previews in the text boxes.
        """
        # Ensure API key is provided and update the client if changed
        key = self.api_key_entry.get().strip()
        if not key:
            messagebox.showerror('Error', 'Please enter your API key in the Configuration panel')
            return
        if key != getattr(self, 'api_key', None):
            self.api_key = key
            self.client = TMDBClient(self.api_key)
        # Validate selected folder
        folder = self.dir_entry.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror('Error', 'Please select a valid directory')
            return
        # Clear previous previews
        self.orig_text.delete('1.0', END)
        self.new_text.delete('1.0', END)
        # Prepare preview lists
        self.file_preview_list: List[Tuple[str, str]] = []
        self.folder_preview_list: List[Tuple[str, str]] = []
        base_name = os.path.basename(folder)
        # Detect folder type: single-movie vs TV-show
        entries = os.listdir(folder)
        subdirs = [d for d in entries if os.path.isdir(os.path.join(folder, d))]
        files_root = [f for f in entries if os.path.isfile(os.path.join(folder, f))]
        # Single movie folder if only one file and no subdirectories
        if not subdirs and len(files_root) == 1:
            f0 = files_root[0]
            movie = parse_movie(f0)
            if movie:
                result = self.client.search_movie(movie['title'], movie['year'])
                if result:
                    title = result.get('title', movie['title'])
                    year = (result.get('release_date') or '')[:4]
                    movie_id = result.get('id')
                    try:
                        imdb = self.client.get_movie_imdb_id(movie_id)
                    except Exception:
                        imdb = None
                    new_name = f"{title} ({year})"
                    if imdb:
                        # Append IMDb ID in Plex-friendly curly braces format
                        new_name += f" {{imdb-{imdb}}}"
                    # Root folder rename
                    self.folder_preview_list.append((base_name, new_name))
        else:
            # TV show folder scenario: detect via any tv parse
            tv_info = None
            for rootp, _, files in os.walk(folder):
                for f in files:
                    tv = parse_tv(f)
                    if tv:
                        tv_info = tv
                        break
                if tv_info:
                    break
            if tv_info:
                result = self.client.search_tv(tv_info['show'])
                show_name = result.get('name', tv_info['show']) if result else tv_info['show']
                year = ''
                if result and result.get('first_air_date'):
                    year = result['first_air_date'][:4]
                tv_id = result.get('id') if result else None
                try:
                    imdb = self.client.get_tv_imdb_id(tv_id) if tv_id else None
                except Exception:
                    imdb = None
                new_show = f"{show_name} ({year})" if year else show_name
                if imdb:
                    # Append IMDb ID in Plex-friendly curly braces format
                    new_show += f" {{imdb-{imdb}}}"
                # Root show folder rename
                self.folder_preview_list.append((base_name, new_show))
                # Season folder renames
                season_map = {}
                for rootp, _, files in os.walk(folder):
                    rel = os.path.relpath(rootp, folder)
                    if rel == '.':
                        continue
                    season_dir = rel.split(os.sep)[0]
                    for f in files:
                        tv = parse_tv(f)
                        if tv:
                            season_map[season_dir] = tv['season']
                for old_dir, season in season_map.items():
                    new_dir = f"Season {season:02}"
                    self.folder_preview_list.append((old_dir, new_dir))
        # Display folder rename previews first
        for old_f, new_f in self.folder_preview_list:
            self.orig_text.insert(END, old_f + '\n')
            self.new_text.insert(END, new_f + '\n')
        # File rename previews
        for rootp, _, files in os.walk(folder):
            rel_dir = os.path.relpath(rootp, folder)
            for f in files:
                old_rel = os.path.join(rel_dir, f) if rel_dir and rel_dir != '.' else f
                new_file = self.get_new_name(f)
                new_rel = os.path.join(rel_dir, new_file) if rel_dir and rel_dir != '.' else new_file
                self.file_preview_list.append((old_rel, new_rel))
                self.orig_text.insert(END, old_rel + '\n')
                self.new_text.insert(END, new_rel + '\n')

    def get_new_name(self, filename: str) -> str:
        """
        Determine the new filename for a single media file based on parsed metadata.

        Args:
            filename: Original file name to parse.

        Returns:
            The proposed new file name (including extension).
        """
        ext = os.path.splitext(filename)[1]
        movie = parse_movie(filename)
        if movie:
            result = self.client.search_movie(movie['title'], movie['year'])
            if result:
                title = result.get('title', movie['title'])
                release_date = result.get('release_date') or ''
                year = release_date[:4] if release_date else None
                if year:
                    return f'{title} ({year}){ext}'
                return f'{title}{ext}'
            # Fallback to parsed info
            if movie.get('year'):
                return f"{movie['title']} ({movie['year']}){ext}"
            return f"{movie['title']}{ext}"
        tv = parse_tv(filename)
        if tv:
            result = self.client.search_tv(tv['show'])
            if result:
                show_name = result.get('name', tv['show'])
                # Attempt to retrieve episode title, but tolerate failures
                try:
                    ep_name = self.client.get_episode_name(result['id'], tv['season'], tv['episode'])
                except Exception:
                    ep_name = None
                # Build filename according to Plex schema
                season_ep = f"S{tv['season']:02}E{tv['episode']:02}"
                if ep_name:
                    return f"{show_name} - {season_ep} - {ep_name}{ext}"
                else:
                    return f"{show_name} - {season_ep}{ext}"
            # Fallback if no TMDB result
            return f"{tv['show']} - S{tv['season']:02}E{tv['episode']:02}{ext}"
        return filename

    def rename_files(self) -> None:
        """
        Rename files on disk according to the prepared preview list, preserving folder structure.
        """
        folder = self.dir_entry.get()
        if not folder:
            return
        errors: List[str] = []
        # Rename files first
        for orig_rel, new_rel in self.file_preview_list:
            src = os.path.join(folder, orig_rel)
            dst = os.path.join(folder, new_rel)
            # create target directories if needed
            dst_dir = os.path.dirname(dst)
            if dst_dir and not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)
            try:
                os.rename(src, dst)
            except Exception as e:
                errors.append(f'File {orig_rel}: {e}')
        # Rename subfolders (e.g., seasons)
        base_name = os.path.basename(folder)
        for old_dir, new_dir in self.folder_preview_list:
            # skip root folder here
            if old_dir == base_name:
                continue
            src = os.path.join(folder, old_dir)
            dst = os.path.join(folder, new_dir)
            try:
                os.rename(src, dst)
            except Exception as e:
                errors.append(f'Folder {old_dir}: {e}')
        # Finally, rename the root folder if needed
        for old_dir, new_dir in self.folder_preview_list:
            if old_dir == base_name:
                parent = os.path.dirname(folder)
                src = folder
                dst = os.path.join(parent, new_dir)
                try:
                    os.rename(src, dst)
                except Exception as e:
                    errors.append(f'Root folder {old_dir}: {e}')
        if errors:
            messagebox.showerror('Errors occurred', '\n'.join(errors))
        else:
            messagebox.showinfo('Success', 'Files renamed successfully')

if __name__ == '__main__':
    app = App()
    app.mainloop()