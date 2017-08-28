# -*- coding: utf-8 -*-
from moviepy.editor import *

class IconManager:
    def __init__(self, resolution=(30,30), length=1.0, padding=10, font='Arial', fontsize=50, txt_position=(0.5, 0.8)):
        self.resolution = resolution
        self.length = length
        self.padding = padding
        self.icon_size = tuple(map(lambda x: x - padding, resolution))
        self.font = font
        self.fontsize = fontsize
        self.txt_position = txt_position
        self.pitch_icon_clip = None
        self.roll_icon_clip = None
        self.battery_icon_clip = None
        self.speed_icon_clip = None
        self.temp_icon_clip = None

    def get_roll_icon_clip(self, angle=0.0):
        if angle is None:
            angle = 0.0
        icon_path = '../data/roll.png'
        if self.roll_icon_clip is None:
            self.roll_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size))

        rotated_icon_clip = (self.roll_icon_clip
                .rotate(float(angle), expand=False)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

        angle_str = '{:.1f}'.format(angle)
        angle_txt_clip = TextClip(angle_str, fontsize=self.fontsize, font=self.font).set_duration(self.length)
        return self.composite_icon_text(rotated_icon_clip, angle_txt_clip, self.txt_position)

    def get_pitch_icon_clip(self, angle=0.0):
        if angle is None:
            angle = 0.0
        icon_path = '../data/pitch.png'
        if self.pitch_icon_clip is None:
            self.pitch_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size))

        rotated_icon_clip = (self.pitch_icon_clip
                .rotate(-float(angle), expand=False)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

        angle_str = '{:.1f}'.format(angle)
        angle_txt_clip = TextClip(angle_str, fontsize=self.fontsize, font=self.font).set_duration(self.length)
        return self.composite_icon_text(rotated_icon_clip, angle_txt_clip, self.txt_position)

    def get_battery_icon_clip(self, charge=0):
        if charge is None:
            charge = 0.0
        icon_path = '../data/battery.png'
        if self.battery_icon_clip is None:
            self.battery_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

        charge_str = '{:d}'.format(charge)
        charge_txt_clip = TextClip(charge_str, fontsize=self.fontsize, font=self.font).set_duration(self.length)
        return self.composite_icon_text(self.battery_icon_clip, charge_txt_clip, self.txt_position)

    def get_speed_icon_clip(self, speed=0.0):
        if speed is None:
            speed = 0.0
        icon_path = '../data/speed.png'
        if self.speed_icon_clip is None:
            self.speed_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

        speed_str = '{:.1f}'.format(speed)
        speed_txt_clip = TextClip(speed_str, fontsize=self.fontsize, font=self.font).set_duration(self.length)
        return self.composite_icon_text(self.speed_icon_clip, speed_txt_clip, self.txt_position)

    def get_temperature_icon_clip(self, temperature=0.0):
        if temperature is None:
            temperature = 0.0
        icon_path = '../data/temp.png'
        if self.temp_icon_clip is None:
            self.temp_icon_clip = (ImageClip(icon_path, duration=self.length)
                .resize(self.icon_size)
                .on_color(col_opacity=0, size=self.resolution, pos=('center')))

        temp_str = '{:.1f}'.format(temperature)
        temp_txt_clip = TextClip(temp_str, fontsize=self.fontsize, font=self.font).set_duration(self.length)
        return self.composite_icon_text(self.temp_icon_clip, temp_txt_clip, self.txt_position)

    def composite_icon_text(self, icon_clip, text_clip, position):
        off_x = text_clip.w / 2.0
        off_y = text_clip.h / 2.0
        txt_pos_in_px = (
            icon_clip.w * position[0] - off_x,
            icon_clip.h * position[1] - off_y
        )
        return CompositeVideoClip([icon_clip, text_clip.set_position(txt_pos_in_px)])
