import customtkinter
import requests
import json
import webbrowser # For opening web links
from PIL import Image # Pillow is needed for CTkImage

# --- Configuration ---
API_KEY = "657f5eb46f757a8ee388acd15f67783a" # Your API Key
LOCATION_CITY = "New York"
LOCATION_COUNTRY_CODE = "US"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={LOCATION_CITY},{LOCATION_COUNTRY_CODE}&appid={API_KEY}&units=imperial"
NYC_EVENTS_URL = "https://www.nycgo.com/things-to-do/events-in-nyc" # Example events page

# --- Activity Suggestions for NYC ---
NYC_ACTIVITIES = {
    "Clear": [
        "Stroll through Central Park.",
        "Walk across the Brooklyn Bridge for great views.",
        "Visit the High Line, an elevated park.",
        "Take the Staten Island Ferry (it's free!) for views of the Statue of Liberty.",
        "Explore Little Island at Pier 55."
    ],
    "Clouds": [
        "Explore Times Square and its vibrant atmosphere.",
        "Visit Top of the Rock or the Empire State Building for city views (check visibility).",
        "Wander through Greenwich Village or SoHo.",
        "Browse the shops on Fifth Avenue.",
        "Visit a food market like Chelsea Market or Smorgasburg (seasonal)."
    ],
    "Rain": [
        "Visit the Metropolitan Museum of Art or the Museum of Modern Art (MoMA).",
        "Catch a Broadway show (check for matinees or last-minute tickets).",
        "Explore Grand Central Terminal's architecture and shops.",
        "Enjoy a cozy cafe or visit the New York Public Library (Stephen A. Schwarzman Building).",
        "Go bowling or visit an indoor entertainment complex."
    ],
    "Drizzle": [
        "Visit the Metropolitan Museum of Art or the Museum of Modern Art (MoMA).",
        "Catch a Broadway show (check for matinees or last-minute tickets).",
        "Explore Grand Central Terminal's architecture and shops.",
        "Enjoy a cozy cafe or visit the New York Public Library (Stephen A. Schwarzman Building).",
        "Browse an independent bookstore."
    ],
    "Snow": [
        "Enjoy ice skating at Rockefeller Center or Bryant Park (seasonal).",
        "Warm up in a museum like the American Museum of Natural History.",
        "See the city transformed under a blanket of snow (if safe to walk).",
        "Find a cozy spot for hot chocolate.",
        "Visit the Tenement Museum for an indoor historical experience."
    ],
    "Mist": [
        "Enjoy a moody walk through a less crowded park.",
        "Visit an art gallery in Chelsea.",
        "Explore an indoor market like Essex Market.",
        "Have a relaxing afternoon tea."
    ],
    "Fog": [
        "Enjoy a moody walk through a less crowded park.",
        "Visit an art gallery in Chelsea.",
        "Explore an indoor market like Essex Market.",
        "Have a relaxing afternoon tea."
    ],
    "Thunderstorm": [
        "Stay indoors! Visit a museum or an indoor attraction.",
        "Watch a movie or catch up on reading.",
        "Order in from one of NYC's many great restaurants."
    ],
    "Extreme": [ # General category for very hot/cold/windy
        "Prioritize indoor activities: museums, galleries, shopping malls.",
        "Check for any weather advisories and stay safe.",
        "If very hot, seek air-conditioned spaces. If very cold, bundle up or stay in."
    ]
}

# --- Event Ideas for NYC (Categories) ---
NYC_EVENT_IDEAS = {
    "Clear": [
        "Look for outdoor concerts or festivals.",
        "Check for street fairs or open-air markets.",
        "See if there are any outdoor movie screenings (seasonal).",
        "Explore neighborhood walking tours."
    ],
    "Clouds": [
        "Good day for gallery openings or art exhibitions.",
        "Check for matinee theater performances.",
        "Look for indoor food festivals or tasting events.",
        "Consider a comedy show in the evening."
    ],
    "Rain": [
        "Perfect for museum special exhibitions or film screenings.",
        "Look for indoor concerts, lectures, or author talks.",
        "Check out indoor craft fairs or conventions.",
        "Many theaters and music venues are great rainy day options."
    ],
    "Drizzle": [ # Similar to rain
        "Perfect for museum special exhibitions or film screenings.",
        "Look for indoor concerts, lectures, or author talks.",
        "Check out indoor craft fairs or conventions."
    ],
    "Snow": [
        "See if there are any holiday markets or winter festivals (seasonal).",
        "Look for cozy indoor music performances.",
        "Some museums or cultural centers might have special winter programs."
    ],
    "General": [ # Fallback for other conditions or if specific ideas are lacking
        "Check online for 'Events in NYC today'.",
        "Look at local news websites for event listings.",
        "Explore official NYC tourism sites for current happenings."
    ]
}


# --- Weather Condition to Icon Mapping (Emojis) ---
WEATHER_ICONS = {
    "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "💧", "Snow": "❄️",
    "Mist": "🌫️", "Fog": "🌫️", "Thunderstorm": "⛈️", "Smoke": "💨", "Haze": "💨",
    "Dust": "💨", "Sand": "💨", "Ash": "💨", "Squall": "💨", "Tornado": "🌪️"
}

class WeatherApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{LOCATION_CITY} Weather & Activity Guide")
        self.geometry("700x700") # Increased height for event ideas
        self.resizable(False, False)

        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")

        font_family_primary = "Bahnschrift"
        font_family_secondary = "Segoe UI"
        font_family_fallback = "Arial"

        self.title_font = customtkinter.CTkFont(family=font_family_primary, size=30, weight="bold")
        self.subtitle_font = customtkinter.CTkFont(family=font_family_primary, size=22, weight="bold")
        self.normal_font = customtkinter.CTkFont(family=font_family_secondary, size=16)
        self.activity_font = customtkinter.CTkFont(family=font_family_secondary, size=14) # Used for both activities and event ideas
        self.icon_font = customtkinter.CTkFont(family=font_family_fallback, size=40)

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.city_label = customtkinter.CTkLabel(self.main_frame, text=f"{LOCATION_CITY.upper()}", font=self.title_font)
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

        # --- Combined Activities and Event Ideas Frame ---
        suggestions_main_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10, fg_color="transparent")
        suggestions_main_frame.pack(pady=10, padx=0, fill="both", expand=True)


        # --- Activity Suggestions Frame ---
        self.activity_frame = customtkinter.CTkFrame(suggestions_main_frame, corner_radius=10)
        self.activity_frame.pack(pady=(0,10), padx=10, fill="both", expand=True) # Takes top half

        activity_title_label = customtkinter.CTkLabel(self.activity_frame, text="Suggested Activities:", font=self.subtitle_font)
        activity_title_label.pack(pady=(10,5), anchor="w", padx=10)
        self.activity_textbox = customtkinter.CTkTextbox(
            self.activity_frame, font=self.activity_font, wrap="word", corner_radius=8, border_spacing=5, height=100
        )
        self.activity_textbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.activity_textbox.configure(state="disabled")

        # --- Event Ideas Frame ---
        self.event_ideas_frame = customtkinter.CTkFrame(suggestions_main_frame, corner_radius=10)
        self.event_ideas_frame.pack(pady=(0,10), padx=10, fill="both", expand=True) # Takes bottom half

        event_ideas_title_label = customtkinter.CTkLabel(self.event_ideas_frame, text="Event Ideas:", font=self.subtitle_font)
        event_ideas_title_label.pack(pady=(10,5), anchor="w", padx=10)
        self.event_ideas_textbox = customtkinter.CTkTextbox(
            self.event_ideas_frame, font=self.activity_font, wrap="word", corner_radius=8, border_spacing=5, height=100
        )
        self.event_ideas_textbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.event_ideas_textbox.configure(state="disabled")

        # --- Buttons Frame ---
        buttons_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0,10), fill="x")


        refresh_button = customtkinter.CTkButton(
            buttons_frame,
            text="Refresh Data",
            command=self.fetch_weather_and_update_ui,
            font=self.normal_font,
            corner_radius=8
        )
        refresh_button.pack(side="left", padx=(10,5), pady=5, expand=True)

        events_link_button = customtkinter.CTkButton(
            buttons_frame,
            text="Find NYC Events Online",
            command=self.open_nyc_events_link,
            font=self.normal_font,
            corner_radius=8
        )
        events_link_button.pack(side="right", padx=(5,10), pady=5, expand=True)


        self.update_theme_colors(None)
        self.fetch_weather_and_update_ui()

    def open_nyc_events_link(self):
        """Opens the NYC_EVENTS_URL in the default web browser."""
        try:
            webbrowser.open_new_tab(NYC_EVENTS_URL)
        except Exception as e:
            print(f"Could not open web browser: {e}")
            # Optionally, show a message in the UI if it fails
            self.event_ideas_textbox.configure(state="normal")
            self.event_ideas_textbox.delete("1.0", "end")
            self.event_ideas_textbox.insert("1.0", f"Could not open browser. Visit:\n{NYC_EVENTS_URL}")
            self.event_ideas_textbox.configure(state="disabled")


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
        self.activity_frame.configure(fg_color=new_bg_color)
        self.event_ideas_frame.configure(fg_color=new_bg_color) # Also theme this new frame

    def fetch_weather_and_update_ui(self):
        current_temp_for_theme = None
        if not API_KEY or API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
            # ... (error handling as before)
            self.update_theme_colors(None)
            self._update_event_ideas_display("API Key needed for weather-based event ideas.", error=True)
            return

        try:
            response_obj = requests.get(WEATHER_URL, timeout=10)
            response_obj.raise_for_status()
            weather_data = response_obj.json()

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

            activities = self.get_activities_for_weather(condition_main, temp)
            self._update_activities_display(activities)

            event_ideas = self.get_event_ideas_for_weather(condition_main) # Get event ideas
            self._update_event_ideas_display(event_ideas) # Display event ideas

            self.update_theme_colors(current_temp_for_theme)

        except requests.exceptions.HTTPError as e:
            # ... (error handling as before, ensure to call self._update_event_ideas_display with error)
            self.update_theme_colors(None)
            self._update_event_ideas_display(f"Could not get event ideas due to weather API error.", error=True)
            # ... (rest of the specific HTTP error handling)
            print(f"HTTP error fetching weather: {e}")
            error_message_detail = "API Key is invalid or not activated.\n1. Double-check the key.\n2. Ensure it's active.\n3. Wait if key is new."
            error_title = "Error: Invalid API Key."
            error_condition = "Authorization Failed (401)."
            error_icon = "🔑❌"

            if e.response is None or e.response.status_code != 401:
                status_code = e.response.status_code if e.response is not None else "Unknown"
                error_message_detail = f"Could not fetch weather data.\nServer Error: {status_code}\nDetails: {e}"
                error_title = "Error: HTTP Problem."
                error_condition = f"Server returned: {status_code}"
                error_icon = "☁️❌"

            self.temp_label.configure(text=error_title)
            self.condition_label.configure(text=error_condition)
            self.weather_icon_label.configure(text=error_icon)
            self._update_activities_display(error_message_detail, error=True) # Keep this for weather error
            self.humidity_label.configure(text="")
            self.wind_label.configure(text="")


        except requests.exceptions.RequestException as e:
            # ... (error handling as before, ensure to call self._update_event_ideas_display with error)
            self.update_theme_colors(None)
            self._update_event_ideas_display(f"Could not get event ideas due to network error.", error=True)
            # ... (rest of the specific network error handling)
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
            
            self.temp_label.configure(text=error_title)
            self.condition_label.configure(text=error_condition)
            self.weather_icon_label.configure(text=error_icon)
            self._update_activities_display(error_message_detail, error=True) # Keep this for weather error
            self.humidity_label.configure(text="")
            self.wind_label.configure(text="")

        except json.JSONDecodeError:
            # ... (error handling as before, ensure to call self._update_event_ideas_display with error)
            self.update_theme_colors(None)
            self._update_event_ideas_display("Could not get event ideas due to data processing error.", error=True)
            # ... (rest of the specific JSON error handling)
            print("Error decoding weather JSON response.")
            self.temp_label.configure(text="Error: Invalid API Response.")
            self.condition_label.configure(text="Data received was not valid JSON.")
            self.weather_icon_label.configure(text="📄❌")
            self._update_activities_display("Error processing weather data from the server. The data format was unexpected.", error=True)
            self.humidity_label.configure(text="")
            self.wind_label.configure(text="")


        except Exception as e:
            # ... (error handling as before, ensure to call self._update_event_ideas_display with error)
            self.update_theme_colors(None)
            self._update_event_ideas_display("Could not get event ideas due to an unexpected error.", error=True)
            # ... (rest of the specific unexpected error handling)
            print(f"An unexpected error occurred: {e}")
            self.temp_label.configure(text="Unexpected Error.")
            self.condition_label.configure(text="Please check the console output.")
            self.weather_icon_label.configure(text="💣")
            self._update_activities_display(f"An unexpected error occurred: {type(e).__name__}\nCheck console for details.", error=True)
            self.humidity_label.configure(text="")
            self.wind_label.configure(text="")


    def get_activities_for_weather(self, main_condition, temperature):
        if temperature is not None:
            if temperature > 86 and main_condition not in ["Rain", "Thunderstorm"]:
                return NYC_ACTIVITIES.get("Extreme", ["Stay cool indoors!"]) + ["Consider indoor activities with AC.", "Stay hydrated."]
            elif temperature < 32 and main_condition not in ["Snow"]:
                return NYC_ACTIVITIES.get("Extreme", ["Bundle up and stay warm!"]) + ["Focus on indoor attractions."]
        if main_condition in NYC_ACTIVITIES: return NYC_ACTIVITIES[main_condition]
        else: # Fallback
            if "Rain" in main_condition or "Drizzle" in main_condition: return NYC_ACTIVITIES["Rain"]
            if "Snow" in main_condition: return NYC_ACTIVITIES["Snow"]
            return NYC_ACTIVITIES.get("Clouds", ["Enjoy the day in NYC! Check local listings for events."]) # Default to clouds if unknown

    def _update_activities_display(self, activities_list, error=False):
        self.activity_textbox.configure(state="normal")
        self.activity_textbox.delete("1.0", "end")
        if error: self.activity_textbox.insert("1.0", activities_list)
        elif activities_list: self.activity_textbox.insert("1.0", "".join([f"• {act}\n" for act in activities_list]))
        else: self.activity_textbox.insert("1.0", "No specific activities suggested.")
        self.activity_textbox.configure(state="disabled")

    def get_event_ideas_for_weather(self, main_condition):
        """Selects event idea categories based on the main weather condition."""
        if main_condition in NYC_EVENT_IDEAS:
            return NYC_EVENT_IDEAS[main_condition]
        else: # Fallback for unlisted conditions
            if "Rain" in main_condition or "Drizzle" in main_condition or "Thunderstorm" in main_condition:
                return NYC_EVENT_IDEAS["Rain"] # Indoor event ideas
            if "Snow" in main_condition:
                return NYC_EVENT_IDEAS["Snow"]
            return NYC_EVENT_IDEAS.get("General", ["Check online for current NYC events."])


    def _update_event_ideas_display(self, event_ideas_list, error=False):
        """Updates the event ideas CtkTextbox."""
        self.event_ideas_textbox.configure(state="normal")
        self.event_ideas_textbox.delete("1.0", "end")
        if error: self.event_ideas_textbox.insert("1.0", event_ideas_list)
        elif event_ideas_list: self.event_ideas_textbox.insert("1.0", "".join([f"• {idea}\n" for idea in event_ideas_list]))
        else: self.event_ideas_textbox.insert("1.0", "No specific event ideas for current conditions.")
        self.event_ideas_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()




