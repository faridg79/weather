"""Import the necessary modules to build the weather app."""
import tkinter as tk
from configparser import ConfigParser
from os import path

import requests
from geopy.geocoders import Nominatim  # type: ignore

# GET API FROM CONFIG FILE
CONFIG_FILE = "config.ini"
config = ConfigParser()
config.read(CONFIG_FILE)
api_key = config["api_key"]["key"]

# IMAGE PATH
img_path = path.join("assets", "images") + path.sep


class WeatherData:
    """Get weather data."""

    def __init__(self, city_name: str):
        """Initialize class WeatherData."""
        get_lat_lon = WeatherData.__get_lat_lon(city_name)
        self.__latitude = get_lat_lon["lat"]
        self.__longitude = get_lat_lon["lon"]

    def current_data(self):
        """Get current weather data."""
        openweather_url = "https://api.openweathermap.org/data/2.5/weather?"
        url = (
            f"{openweather_url}"
            f"lat={self.__latitude}&lon={self.__longitude}"
            f"&units=metric&appid={api_key}"
        )
        res = requests.get(
            url,
            "GET",
            timeout=5,
        )
        json = res.json()
        return {
            "weather": json["weather"][0]["main"],
            "description": json["weather"][0]["description"],
            "icon": json["weather"][0]["icon"],
            "temp": json["main"]["temp"],
            "feels_like": json["main"]["feels_like"],
            "temp_min": json["main"]["temp_min"],
            "temp_max": json["main"]["temp_max"],
            "pressure": json["main"]["pressure"],
            "humidity": json["main"]["humidity"],
            "wind": json["wind"]["speed"],
            "visibility": json["visibility"],
        }

    def forecast_data(self):
        """Get forecast weather data."""
        return "test"

    @staticmethod
    def __get_lat_lon(city_name: str) -> dict:
        """Get longitude and latitude."""
        geolocator = Nominatim(user_agent="App weather")
        location = geolocator.geocode(city_name)
        return {
            "lat": location.latitude,
            "lon": location.longitude,
        }


class WeatherApp:
    """Class to manage the app and UI."""

    def __init__(
        self,
        screen_size: str,
        screen_title: str,
        icon_name: str,
    ) -> None:
        """Initialize the app."""
        self.root = tk.Tk()
        # ADD SCREEN SIZE
        self.root.geometry(screen_size)
        self.root.resizable(False, False)
        # ADD TITLE
        self.root.title(screen_title)
        # ADD IMAGE ICON
        icon = tk.PhotoImage(file=img_path + icon_name)
        self.root.iconphoto(False, icon)
        # ADD BG APP
        self.root.configure(bg="#204c8a")
        # LOAD IMAGES
        self.images = {
            "search_bar_bg": WeatherApp.__load_image("search.png"),
            "search_icon": WeatherApp.__load_image("loupe.png"),
            "location": WeatherApp.__load_image("location.png"),
            "current_bg": WeatherApp.__load_image("cr_img.png"),
        }
        # CITY NAME
        self.__city_name = tk.StringVar()

        # SEARCH BAR
        self.search_bar()
        self.root.mainloop()

    def search_bar(self):
        """Set search bar for app."""
        # BACKGROUND SEARCH BAR
        search_bg = tk.Label(
            self.root,
            bg="#171717",
        )
        search_bg.place(
            x=0,
            y=0,
            width=980,
            height=46,
        )

        # SHOW CITY_NAME IN SEARCH BAR
        self.city_name_lbl = tk.Label(
            self.root,
            font=("Roboto Bold", 15),
            bg="#171717",
            fg="#fefefe",
        )
        self.city_name_lbl.place(
            x=20,
            y=6,
        )

        # BACKGROUND SEARCH INPUT
        search_entry_bg = tk.Label(
            self.root,
            image=self.images["search_bar_bg"],
            borderwidth=0,
            bg="#171717",
        )
        search_entry_bg.place(
            x=670,
            y=7,
        )

        # ICON SEARCH + BUTTON SEARCH
        search_btn = tk.Button(
            self.root,
            image=self.images["search_icon"],
            borderwidth=0,
            bg="#fefefe",
            activebackground="#fefefe",
            command=self.set_current_weather,
        )
        search_btn.place(
            x=940,
            y=11,
        )

        # SEARCH INPUT
        search_entry = tk.Entry(
            self.root,
            textvariable=self.__city_name,
            font=("Roboto Regular", 11),
            bg="#fefefe",
            border=0,
            justify="center",
            insertbackground="#171717",
        )
        search_entry.place(
            x=720,
            y=11,
            width=200,
        )

        # LOCATION ICON
        location_icon_lbl = tk.Label(
            self.root,
            image=self.images["location"],
            bg="#fefefe",
            border=0,
        )
        location_icon_lbl.place(
            x=679,
            y=11,
        )

    def set_current_weather(self):
        """Set current weather."""
        get_data = WeatherData(self.__city_name.get()).current_data()
        self.city_name_lbl.configure(
            text=self.__city_name.get().title(),
        )
        my_var = {
            "wind": (int(get_data["wind"]) * 3600) / 1000,
            "feels_like": str(int(get_data["feels_like"])),
            "vis": int(get_data["visibility"]),
        }
        frame = tk.Frame(
            self.root,
            width=490,
            height=230,
            bg="#204c8a",
        )
        frame.place(
            x=40,
            y=80,
        )
        cr_lbl = tk.Label(
            frame,
            image=self.images["current_bg"],
            bg="#204c8a",
        )
        cr_lbl.place(
            x=0,
            y=0,
        )
        cr_weather_text = tk.Label(
            frame,
            text="Current weather",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Bold", 11),
        )
        cr_weather_text.place(
            x=9,
            y=13,
        )
        self.images["current_icon"] = WeatherApp.__load_image(
            get_data["icon"] + ".png",
        )
        cr_weather_icon_lbl = tk.Label(
            frame,
            image=self.images["current_icon"],
            bg="#174384",
        )
        cr_weather_icon_lbl.place(
            x=2,
            y=35,
        )
        cr_temp_text = tk.Label(
            frame,
            text=str(int(get_data["temp"])) + "°",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 40),
        )
        cr_temp_text.place(
            x=95,
            y=55,
        )
        main_weather = tk.Label(
            frame,
            text=get_data["weather"],
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Black", 12),
        )
        main_weather.place(
            x=199,
            y=65,
        )

        feels_like = tk.Label(
            frame,
            text=f"feels like  {my_var['feels_like']}°",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 10),
        )
        feels_like.place(
            x=199,
            y=90,
        )
        description = tk.Label(
            frame,
            text=get_data["description"]
            + ". The high will be "
            + str(int(get_data["temp_max"]))
            + "°",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 10),
        )
        description.place(
            x=10,
            y=128,
        )

        wind_speed = tk.Label(
            frame,
            text=f"Wind\n {int(my_var['wind'])} km/h",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 10),
        )
        wind_speed.place(
            x=10,
            y=165,
        )
        humidity = tk.Label(
            frame,
            text=f"Humidity\n {get_data['humidity']}%",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 10),
        )
        humidity.place(
            x=90,
            y=165,
        )
        visibility = tk.Label(
            frame,
            text=f"Visibility\n {my_var['vis'] / 1000:.0f} km",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 10),
        )
        visibility.place(
            x=170,
            y=165,
        )
        pressure = tk.Label(
            frame,
            text=f"Pressure\n {int(get_data['pressure'])} mb",
            bg="#174384",
            fg="#fefefe",
            font=("Roboto Regular", 10),
        )
        pressure.place(
            x=250,
            y=165,
        )

    @staticmethod
    def __load_image(img_name: str):
        return tk.PhotoImage(
            file=img_path + img_name,
        )


b = WeatherApp("980x580+100+20", "Weather app - Karyar", "icon.png")
