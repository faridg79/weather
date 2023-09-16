"""Import the necessary modules to build the weather app."""
import tkinter as tk
from configparser import ConfigParser
from datetime import datetime
from os import path

import requests
from geopy.geocoders import Nominatim  # type: ignore
from PIL import Image, ImageTk

# GET API FROM CONFIG FILE
CONFIG_FILE = "config.ini"
config = ConfigParser()
config.read(CONFIG_FILE)
api_key = config["api_key"]["key"]

# IMAGE PATH
img_path = path.join("assets", "images") + path.sep

# CURRENT DATETIME
current_datetime = datetime.now()
current_datetime = current_datetime.replace(
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
)
day_of_month = current_datetime.strftime("%d")  # 02
day_name = current_datetime.strftime("%a")  # Thu
cr_date = day_name + " " + day_of_month


class WeatherData:
    """Get weather data."""

    def __init__(self, city_name: str):
        """Initialize class WeatherData."""
        self.geolocator = Nominatim(user_agent="App weather")
        get_lat_lon = self.__get_lat_lon(city_name)
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
            timeout=15,
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

    def future_data(self):
        """Get future weather data."""
        openweather_url = "https://api.openweathermap.org/data/2.5/forecast?"
        url = (
            f"{openweather_url}"
            f"lat={self.__latitude}&lon={self.__longitude}"
            f"&units=metric&appid={api_key}"
        )
        res = requests.get(
            url,
            "GET",
            timeout=10,
        )
        json = res.json()
        daily_weather = []
        for item in json["list"]:
            date_time = datetime.utcfromtimestamp(item["dt"])

            if date_time.hour == 12 and date_time > current_datetime:
                daily_weather.append(item)
        daily_list = []
        for weather in daily_weather:
            dt_txt = weather["dt_txt"]
            weather_datetime = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            days_of_the_week = weather_datetime.strftime("%a")
            days_of_the_month = weather_datetime.strftime("%d")
            date_day = days_of_the_week + " " + days_of_the_month
            daily_list.append(
                {
                    "date": date_day,
                    "temp": weather["main"]["temp"],
                    "humidity": weather["main"]["humidity"],
                    "icon": weather["weather"][0]["icon"],
                },
            )
        return daily_list

    def get_info_city(self):
        """Get Info about city."""
        location = self.geolocator.reverse(
            str(self.__latitude) + "," + str(self.__longitude),
            language="en",
        )
        address = location.raw["address"]
        city = address.get("city", "").title()
        if "province" in address:
            state = address["province"].title()
        else:
            state = address["state"].title()

        country = address.get("country", "").title()
        return {
            "city": city + ", ",
            "state": state + ", ",
            "country": country,
        }

    def __get_lat_lon(self, city_name: str) -> dict:
        """Get longitude and latitude."""
        location = self.geolocator.geocode(city_name)
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
            "cr_w_bg": WeatherApp.__load_image("cr_w_bg.png"),
            "other_w_bg": WeatherApp.__load_image("other_w_bg.png"),
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
        city_name_lbl = tk.Label(
            self.root,
            text="Forecast",
            font=("Roboto Bold", 15),
            bg="#171717",
            fg="#fefefe",
        )
        city_name_lbl.place(
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
        self.city_info_data = tk.Label(
            self.root,
            bg="#204c8a",
            fg="#fefefe",
            font=("Roboto Regular", "10"),
        )
        self.city_info_data.place(
            x=40,
            y=50,
        )

    def set_current_weather(self):
        """Set current weather."""
        get_data = WeatherData(self.__city_name.get()).current_data()
        my_var = {
            "wind": (int(get_data["wind"]) * 3600) / 1000,
            "feels_like": str(int(get_data["feels_like"])),
            "vis": int(get_data["visibility"]),
            "get_info_city": WeatherData(
                self.__city_name.get(),
            ).get_info_city(),
        }
        self.city_info_data.configure(
            text=my_var["get_info_city"]["city"]
            + my_var["get_info_city"]["state"]
            + my_var["get_info_city"]["country"],
        )
        frame = tk.Frame(
            self.root,
            width=490,
            height=220,
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
        self.set_daily_weather(
            get_data,
            WeatherData(self.__city_name.get()).future_data(),
        )

    def set_daily_weather(
        self,
        get_data: dict,
        future_data: list,
    ):
        """Set daily weather."""
        # SET FRAME
        frame = tk.Frame(
            self.root,
            width=980,
            height=150,
            bg="#204c8a",
        )
        frame.place(
            x=40,
            y=300,
        )
        # LABEL TITLE
        title_lbl = tk.Label(
            frame,
            fg="#fefefe",
            bg="#204c8a",
            font=("Roboto Bold", 10),
            text="5 DAY FORECAST",
        )
        title_lbl.place(
            x=0,
            y=0,
        )

        def current_weather_box():
            # BOX CURRENT
            box_cr = tk.Frame(
                frame,
                bg="#204c8a",
            )
            box_cr.place(
                x=0,
                y=25,
                width=230,
                height=120,
            )
            bg_box_cr = tk.Label(
                box_cr,
                bg="#204c8a",
                image=self.images["cr_w_bg"],
                border=0,
            )
            bg_box_cr.place(
                x=0,
                y=0,
            )

            date_lbl_one = tk.Label(
                box_cr,
                fg="#fefefe",
                font=("Roboto Regular", 9),
                text="Today",
                bg="#315793",
            )
            date_lbl_one.place(
                x=10,
                y=5,
            )
            self.images["cr_resized_image"] = ImageTk.PhotoImage(
                self.resize_image(
                    Image.open(
                        img_path + get_data["icon"] + ".png",
                    ),
                    60,
                    60,
                ),
            )
            icon_lbl_one = tk.Label(
                box_cr,
                image=self.images["cr_resized_image"],
                bg="#315793",
            )
            icon_lbl_one.place(
                x=8,
                y=25,
                width=60,
                height=60,
            )
            temp_lbl_one = tk.Label(
                box_cr,
                fg="#fefefe",
                font=("Roboto Bold", 9),
                text=f"{get_data['temp_max']:.0f}°",
                bg="#315793",
            )
            temp_lbl_one.place(
                x=75,
                y=32,
            )
            humidity_lbl_one = tk.Label(
                box_cr,
                fg="#fefefe",
                font=("Roboto Bold", 9),
                text=f"{get_data['humidity']}%",
                bg="#315793",
            )
            humidity_lbl_one.place(
                x=75,
                y=55,
            )
            weather_lbl_one = tk.Label(
                box_cr,
                fg="#fefefe",
                font=("Roboto Bold", 10),
                text=f"{get_data['weather']}",
                bg="#315793",
            )
            weather_lbl_one.place(
                x=125,
                y=41,
            )

        current_weather_box()
        # SHOW OTHER DAYS WEATHER
        x_box = 240
        for weather in future_data:
            box_future = tk.Frame(
                frame,
                bg="#204c8a",
                width=120,
                height=118,
            )
            box_future.place(
                x=x_box,
                y=25,
            )
            box_future_bg = tk.Label(
                box_future,
                bg="#204c8a",
                image=self.images["other_w_bg"],
                border=0,
            )
            box_future_bg.pack()

            date_lbl_one = tk.Label(
                box_future,
                fg="#fefefe",
                font=("Roboto Regular", 9),
                text=weather["date"],
                bg="#315793",
            )
            date_lbl_one.place(
                x=10,
                y=5,
            )
            self.images["fu_resized_img" + str(x_box)] = ImageTk.PhotoImage(
                self.resize_image(
                    Image.open(
                        img_path + weather["icon"] + ".png",
                    ),
                    60,
                    60,
                ),
            )
            icon_lbl_one = tk.Label(
                box_future,
                image=self.images["fu_resized_img" + str(x_box)],
                bg="#315793",
            )
            icon_lbl_one.place(
                x=8,
                y=25,
                width=60,
                height=60,
            )
            temp_lbl_one = tk.Label(
                box_future,
                fg="#fefefe",
                font=("Roboto Bold", 9),
                text=f"{weather['temp']:.0f}°",
                bg="#315793",
            )
            temp_lbl_one.place(
                x=75,
                y=32,
            )
            humidity_lbl_one = tk.Label(
                box_future,
                fg="#fefefe",
                font=("Roboto Bold", 9),
                text=f"{weather['humidity']}%",
                bg="#315793",
            )
            humidity_lbl_one.place(
                x=75,
                y=55,
            )
            x_box += 130

    @staticmethod
    def __load_image(img_name: str):
        return tk.PhotoImage(
            file=img_path + img_name,
        )

    @staticmethod
    def resize_image(image, new_width, new_height):
        """Resize images."""
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


b = WeatherApp("980x630+100+10", "Weather app - Karyar", "icon.png")
