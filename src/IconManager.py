# -*- coding: utf-8 -*-
from moviepy.editor import *

class IconManager:
    def __init__(self, resolution=(30,30), length=1.0, padding=10):
        self.resolution = resolution
        self.length = length
        self.padding = padding
        self.icon_size = tuple(map(lambda x: x - padding, resolution))
        self.pitch_icon_clip = None
        self.roll_icon_clip = None
        self.battery_icon_clip = None
        self.speed_icon_clip = None
        self.temp_icon_clip = None

    def get_roll_icon_clip(self, angle=0.0):
        icon_path = '../data/roll.png'
        if self.roll_icon_clip is None:
            self.roll_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size))

        return (self.roll_icon_clip
                .rotate(float(angle), expand=False)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

    def get_pitch_icon_clip(self, angle=0.0):
        icon_path = '../data/pitch.png'
        if self.pitch_icon_clip is None:
            self.pitch_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size))

        return (self.pitch_icon_clip
                .rotate(-float(angle), expand=False)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

    def get_battery_icon_clip(self, charge=0):
        icon_path = '../data/battery.png'
        if self.battery_icon_clip is None:
            self.battery_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))
        return self.battery_icon_clip

    def get_speed_icon_clip(self, speed=0.0):
        icon_path = '../data/speed.png'
        if self.speed_icon_clip is None:
            self.speed_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))
        return self.speed_icon_clip

    def get_temperature_icon_clip(self, temperature=0.0):
        icon_path = '../data/temp.png'
        if self.temp_icon_clip is None:
            self.temp_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))
        return self.temp_icon_clip
