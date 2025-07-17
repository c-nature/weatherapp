import customtkinter
import requests
import json
import webbrowser
from PIL import Image # Pillow is needed for CTkImage
import os # Import the os module to access environment variables

# --- Configuration ---
OPENWEATHER_API_KEY = "657f5eb46f757a8ee388acd15f67783a" # Your OpenWeatherMap API Key
# Get PredictHQ API Key from environment variable
PREDICTHQ_API_KEY = os.environ.get("PREDICTHQ_API_KEY") 
PREDICTHQ_API_URL = "https://api.predicthq.com/v1/events/" # Base URL for PredictHQ Events API

WEATHER_URL_TEMPLATE = "http://api.openweathermap.org/data/2.5/weather?zip={zip_code},{country_code}&appid={API_KEY}&units=imperial"

# --- Weather Condition to Icon Mapping (Emojis) ---
WEATHER_ICONS = {
    "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "💧", "Snow": "❄️",
    "Mist": "🌫️", "Fog": "🌫️", "Thunderstorm": "⛈️", "Smoke": "💨", "Haze": "🌫️",
    "Dust": "💨", "Sand": "💨", "Ash": "💨", "Squall": "💨", "Tornado": "🌪️"
}

# --- PredictHQ API Function ---
def fetch_predicthq_events(zip_code, radius_miles=10):
    """
    Fetches events from PredictHQ API based on ZIP code and radius.

    Args:
        zip_code (str): The ZIP code for the event search.
        radius_miles (int): The radius for the search in miles.

    Returns:
        list: A list of dictionaries, each representing an event, or an empty list if an error occurs.
    """
    # Check if API key is set
    if not PREDICTHQ_API_KEY:
        print("Error: PredictHQ API Key is not set in environment variables. Cannot fetch events.")
        return []

    headers = {
        "Authorization": f"Bearer {PREDICTHQ_API_KEY}",
        "Accept": "application/json",
    }
    params = {
        "q": "event", # General query for events
        "location_around.zip": zip_code,
        "location_around.radius": f"{radius_miles}mi",
        "active.gte": "now", # Only get active or future events
        "limit": 10 # Limit results for display
    }

    try:
        response = requests.get(PREDICTHQ_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        events = []
        for event in data.get("results", []):
            event_name = event.get("title", "No Title")
            event_url = event.get("url", "#") # PredictHQ provides a direct URL for the event
            start_time = event.get("start", "N/A")
            end_time = event.get("end", "N/A")
            
            # PredictHQ venue details might be in 'entities' or directly in 'location'
            # For simplicity, we'll try to get location description or just coordinates
            location_description = event.get("entities", [])[0].get("name") if event.get("entities") else "N/A"
            if location_description == "N/A" and event.get("location"):
                location_description = f"Lat: {event['location'][1]}, Lon: {event['location'][0]}"

            events.append({
                "name": event_name,
                "url": event_url,
                "start_time": start_time,
                "end_time": end_time,
                "location_description": location_description
            })
        return events

    except requests.exceptions.HTTPError as e:
        print(f"PredictHQ API HTTP Error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 401:
            print("PredictHQ Authentication Error: Check your API Key and ensure it's correctly set as an environment variable.")
        elif e.response.status_code == 400:
            print(f"PredictHQ Bad Request: {e.response.json().get('detail', 'No detail provided')}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"PredictHQ API Network Error: {e}")
        return []
    except json.JSONDecodeError:
        print("PredictHQ API: Error decoding JSON response.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred with PredictHQ API: {e}")
        return []


class WeatherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Weather & Event Guide")
        self.geometry("700x700")
        self.resizable(False, False)

        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")

        font_family_primary = "Bahnschrift"
        font_family_secondary = "Segoe UI"
        font_family_fallback = "Arial"

        self.title_font = customtkinter.CTkFont(family=font_family_primary, size=30, weight="bold")
        self.subtitle_font = customtkinter.CTkFont(family=font_family_primary, size=22, weight="bold")
        self.normal_font = customtkinter.CTkFont(family=font_family_secondary, size=16)
        self.event_font = customtkinter.CTkFont(family=font_family_secondary, size=14)
        self.icon_font = customtkinter.CTkFont(family=font_family_fallback, size=40)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- Location Input Frame ---
        location_input_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        location_input_frame.pack(pady=(10, 5), padx=10, fill="x")

        self.zip_label = customtkinter.CTkLabel(location_input_frame, text="Enter ZIP Code:", font=self.normal_font)
        self.zip_label.pack(side="left", padx=(0, 10))

        self.zip_code_entry = customtkinter.CTkEntry(location_input_frame, placeholder_text="e.g., 10001", width=120, font=self.normal_font)
        self.zip_code_entry.pack(side="left", padx=(0, 10))
        self.zip_code_entry.insert(0, "10001") # Default to a NYC ZIP code

        self.fetch_button = customtkinter.CTkButton(
            location_input_frame,
            text="Get Data",
            command=self.fetch_data_and_update_ui,
            font=self.normal_font,
            corner_radius=8
        )
        self.fetch_button.pack(side="left", padx=(0, 0))

        self.city_label = customtkinter.CTkLabel(self.main_frame, text="LOCATION", font=self.title_font)
        self.city_label.pack(pady=(10, 5))

        self.weather_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10)
        self.weather_frame.pack(pady=10, padx=10, fill="x")

        self.weather_icon_label = customtkinter.CTkLabel(self.weather_frame, text="⏳", font=self.icon_font)
        self.weather_icon_label.pack(side="left", padx=20, pady=10)

        weather_details_frame = customtkinter.CTkFrame(self.weather_frame, fg_color="transparent")
        weather_details_frame.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.temp_label = customtkinter.CTkLabel(weather_details_frame, text="Temperature: --°F", font=self.subtitle_font)
        self.temp_label.pack(anchor="w")
        self.condition_label = customtkinter.CTkLabel(weather_details_frame, text="Condition: ----", font=self.normal_font)
        self.condition_label.pack(anchor="w")
        self.humidity_label = customtkinter.CTkLabel(weather_details_frame, text="Humidity: --%", font=self.normal_font)
        self.humidity_label.pack(anchor="w")
        self.wind_label = customtkinter.CTkLabel(weather_details_frame, text="Wind: -- mph", font=self.normal_font)
        self.wind_label.pack(anchor="w")

        # --- PredictHQ Events Frame ---
        self.eventbrite_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10) # Reusing this frame
        self.eventbrite_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Updated title to reflect PredictHQ
        predicthq_title_label = customtkinter.CTkLabel(self.eventbrite_frame, text="Local Events (PredictHQ):", font=self.subtitle_font)
        predicthq_title_label.pack(pady=(10,5), anchor="w", padx=10)

        self.eventbrite_textbox = customtkinter.CTkTextbox(
            self.eventbrite_frame, font=self.event_font, wrap="word", corner_radius=8, border_spacing=5, height=150
        )
        self.eventbrite_textbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.eventbrite_textbox.configure(state="disabled")
        self.event_links_map = {}
        self.eventbrite_textbox.bind("<Button-1>", self._on_event_link_click)

        self.update_theme_colors(None)
        self.fetch_data_and_update_ui() # Initial data fetch on startup

    def _on_event_link_click(self, event):
        """Handles clicks on event links within the eventbrite_textbox (now PredictHQ events)."""
        try:
            index = self.eventbrite_textbox.index(f"@{event.x},{event.y}")
            tags = self.eventbrite_textbox.tag_names(index)
            
            for tag in tags:
                if tag.startswith("event_link_"):
                    url = self.event_links_map.get(tag)
                    if url:
                        webbrowser.open_new_tab(url)
                        return
        except Exception as e:
            print(f"Error handling event link click: {e}")

    def get_color_for_temperature(self, temperature_f):
        if temperature_f is None: return "#E5E5E5"
        if temperature_f <= -10: return "#E0F2FE"
        elif temperature_f <= 15: return "#D4E6F1"
        elif temperature_f <= 32: return "#BDE6F1"
        elif temperature_f <= 50: return "#E6E0F8"
        elif temperature_f <= 65: return "#D1F2EB"
        elif temperature_f <= 75: return "#FEF9E7"
        elif temperature_f <= 85: return "#FFE4C4"
        elif temperature_f <= 95: return "#FFD1DC"
        else: return "#FFBCAD"

    def update_theme_colors(self, temperature_f):
        new_bg_color = self.get_color_for_temperature(temperature_f)
        self.configure(fg_color=new_bg_color)
        self.main_frame.configure(fg_color=new_bg_color)
        self.weather_frame.configure(fg_color=new_bg_color)
        self.eventbrite_frame.configure(fg_color=new_bg_color)

    def fetch_data_and_update_ui(self):
        """Fetches weather and PredictHQ event data based on ZIP code."""
        zip_code = self.zip_code_entry.get().strip()
        if not zip_code:
            self.city_label.configure(text="Please enter a ZIP code.")
            self._update_weather_display_error("Invalid Input", "Please enter a ZIP code.", "🚫")
            self._update_predicthq_display("Please enter a ZIP code to find events.")
            self.update_theme_colors(None)
            return

        current_temp_for_theme = None
        weather_url = WEATHER_URL_TEMPLATE.format(zip_code=zip_code, country_code="US", API_KEY=OPENWEATHER_API_KEY)

        # --- Fetch Weather Data ---
        if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
            self.city_label.configure(text="Weather API Key Missing!")
            self._update_weather_display_error("API Key Needed", "Please provide your OpenWeatherMap API Key.", "🔑❌")
            self.update_theme_colors(None)
        else:
            try:
                response_obj = requests.get(weather_url, timeout=10)
                response_obj.raise_for_status()
                weather_data = response_obj.json()

                city_name = weather_data.get("name", "Unknown City")
                self.city_label.configure(text=f"{city_name.upper()}")

                temp = weather_data.get("main", {}).get("temp")
                current_temp_for_theme = temp
                condition_main = weather_data.get("weather", [{}])[0].get("main", "N/A")
                condition_desc = weather_data.get("weather", [{}])[0].get("description", "Not available")
                humidity = weather_data.get("main", {}).get("humidity")
                wind_speed = weather_data.get("wind", {}).get("speed")

                self.temp_label.configure(text=f"Temperature: {temp}°F" if temp is not None else "Temperature: --°F")
                self.condition_label.configure(text=f"Condition: {condition_desc.capitalize()}")
                self.weather_icon_label.configure(text=WEATHER_ICONS.get(condition_main, "❓"))
                self.humidity_label.configure(text=f"Humidity: {humidity}%" if humidity is not None else "Humidity: --%")
                self.wind_label.configure(text=f"Wind: {wind_speed} mph" if wind_speed is not None else "Wind: -- mph")

                self.update_theme_colors(current_temp_for_theme)
                
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else "Unknown"
                error_icon = "☁️❌"
                error_title = "Error: HTTP Problem."
                error_condition = f"Server returned: {status_code}"
                error_message_detail = f"Could not fetch weather data.\nServer Error: {status_code}\nDetails: {e}"

                if status_code == 401:
                    error_message_detail = "API Key is invalid or not activated.\n1. Double-check the key.\n2. Ensure it's active.\n3. Wait if key is new."
                    error_title = "Error: Invalid API Key."
                    error_condition = "Authorization Failed (401)."
                    error_icon = "🔑❌"
                elif status_code == 404:
                    error_message_detail = f"ZIP code '{zip_code}' not found by weather service."
                    error_title = "Error: Location Not Found."
                    error_condition = "Invalid ZIP Code."
                    error_icon = "📍❌"
                    self.city_label.configure(text="Unknown Location")

                print(f"HTTP error fetching weather: {e}")
                self._update_weather_display_error(error_title, error_condition, error_icon)
                self.update_theme_colors(None)

            except requests.exceptions.RequestException as e:
                print(f"Network error fetching weather: {e}")
                error_message_detail = "Could not resolve server. Check internet connection & DNS settings."
                error_title = "Error: DNS Resolution Failed."
                error_condition = "Cannot find api.openweathermap.org."
                error_icon = "🌐❌"

                if not ("NameResolutionError" in str(e) or "[Errno 11001]" in str(e) or "nodename nor servname provided" in str(e).lower()):
                    error_message_detail = f"Could not connect to weather service.\nNetwork Error: {type(e).__name__}"
                    error_title = "Error: Connection Failed."
                    error_condition = "Check internet connection."
                    error_icon = "🔌❌"
                
                self._update_weather_display_error(error_title, error_condition, error_icon)
                self.update_theme_colors(None)

            except json.JSONDecodeError:
                print("Error decoding weather JSON response.")
                self._update_weather_display_error("Error: Invalid API Response.", "Data received was not valid JSON.", "📄❌")
                self.update_theme_colors(None)

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self._update_weather_display_error("Unexpected Error.", "Please check the console output.", "💣")
                self.update_theme_colors(None)

        # --- Fetch PredictHQ Events ---
        if not PREDICTHQ_API_KEY: # Changed condition to check for None/empty string
            self._update_predicthq_display("PredictHQ API Key is missing or invalid. Cannot fetch events. Please set the PREDICTHQ_API_KEY environment variable.")
        else:
            self._update_predicthq_display("Fetching local events from PredictHQ...")
            events = fetch_predicthq_events(zip_code)
            self._update_predicthq_display(events=events)


    def _update_weather_display_error(self, title, condition, icon):
        """Helper to update weather display with error messages."""
        self.temp_label.configure(text=title)
        self.condition_label.configure(text=condition)
        self.weather_icon_label.configure(text=icon)
        self.humidity_label.configure(text="")
        self.wind_label.configure(text="")

    def _update_predicthq_display(self, message=None, events=None):
        """Updates the eventbrite_textbox (now PredictHQ events textbox) with event information or a message."""
        self.eventbrite_textbox.configure(state="normal")
        self.eventbrite_textbox.delete("1.0", "end")
        self.event_links_map = {} # Reset map for new content

        if message:
            self.eventbrite_textbox.insert("1.0", message + "\n\n")
        
        if events:
            if not events:
                self.eventbrite_textbox.insert("end", "No PredictHQ events found for this location within 10 miles.\n")
            else:
                for i, event in enumerate(events):
                    event_name = event.get("name", "N/A")
                    event_url = event.get("url", "#")
                    start_time = event.get("start_time", "N/A")
                    location_desc = event.get("location_description", "N/A")

                    self.eventbrite_textbox.insert("end", f"Event: ", "event_text")
                    tag_name = f"event_link_{i}"
                    self.eventbrite_textbox.insert("end", f"{event_name}\n", tag_name)
                    self.eventbrite_textbox.tag_config(tag_name, foreground="blue", underline=True)
                    self.event_links_map[tag_name] = event_url
                    
                    self.eventbrite_textbox.insert("end", f"  When: {start_time}\n")
                    self.eventbrite_textbox.insert("end", f"  Where: {location_desc}\n\n")
        
        self.eventbrite_textbox.configure(state="disabled")


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
