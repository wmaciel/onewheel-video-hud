# -*- coding: utf-8 -*-
from moviepy.editor import *


class IconManager:
    def __init__(self, resolution=(30, 30), padding=10, font='Arial',
                 fontsize=50, txt_position=(0.5, 0.8), unit_position=(0.5, 0.2), unit='metric'):
        self.resolution = resolution
        self.padding = padding
        self.icon_size = tuple(map(lambda x: x - padding, resolution))
        self.font = font
        self.fontsize = fontsize
        self.txt_position = txt_position
        self.pitch_icon_clip = None
        self.roll_icon_clip = None
        self.battery_icon_clip = None
        self.speed_icon_clip = None
        self.speed_icon_bg_clip = None
        self.speed_icon_pointer_clip = None
        self.temp_icon_clip = None
        self.units = {
            'metric': {
                'speed': 'Km/h',
                'temperature': '°C'
            },
            'imperial': {
                'speed': 'M.P.H.',
                'temperature': '°F'
            }
        }
        self.unit = self.units[unit]
        self.unit_position = unit_position
        self.cached_clips = {
            'roll': {},
            'pitch': {},
            'speed': {},
            'battery': {},
            'temperature': {}
        }

    def get_roll_icon_clip(self, angle=0.0, duration=1.0):
        # fixes invalid angle value
        if angle is None:
            angle = 0.0

        # generate the angle string from string value
        angle_str = '{:.1f}'.format(angle)

        # if we have a cache hit, use the cached value
        if angle_str in self.cached_clips['roll']:
            return self.cached_clips['roll'][angle_str]

        # else, create a new clip
        if self.roll_icon_clip is None:
            icon_path = '../data/roll.png'
            self.roll_icon_clip = (ImageClip(icon_path, duration=duration)
                                   .resize(self.icon_size))
        else:
            self.roll_icon_clip = self.roll_icon_clip.set_duration(duration)

        # rotate it as needed
        rotated_icon_clip = (self.roll_icon_clip
                             .rotate(float(angle), expand=False)
                             .on_color(col_opacity=0, size=self.resolution, pos='center'))

        # generate a new text to go with the icon
        angle_txt_clip = TextClip(angle_str, fontsize=self.fontsize, font=self.font).set_duration(duration)
        new_icon_clip = self.composite_icon_text(rotated_icon_clip, angle_txt_clip, self.txt_position)

        # add it to the cache
        self.cached_clips['roll'][angle_str] = new_icon_clip

        # return it
        return new_icon_clip

    def get_pitch_icon_clip(self, angle=0.0, duration=1.0):
        # fixes invalid angle value
        if angle is None:
            angle = 0.0

        # generate the angle string from string value
        angle_str = '{:.1f}'.format(angle)

        # if we have a cache hit, use the cached value
        if angle_str in self.cached_clips['pitch']:
            return self.cached_clips['pitch'][angle_str]

        # else, create a new clip
        if self.pitch_icon_clip is None:
            icon_path = '../data/pitch.png'
            self.pitch_icon_clip = (ImageClip(icon_path, duration=duration)
                                    .resize(self.icon_size)
                                    .on_color(col_opacity=0, size=self.resolution, pos='center'))
        else:
            self.pitch_icon_clip = self.pitch_icon_clip.set_duration(duration)

        # rotate it as needed
        rotated_icon_clip = (self.pitch_icon_clip
                             .rotate(float(angle), expand=False)
                             .resize(self.resolution))

        # generate a new text to go with the icon
        angle_txt_clip = TextClip(angle_str, fontsize=self.fontsize, font=self.font).set_duration(duration)
        new_icon_clip = self.composite_icon_text(rotated_icon_clip, angle_txt_clip, self.txt_position)

        # add it to the cache
        self.cached_clips['pitch'][angle_str] = new_icon_clip

        # return it
        return new_icon_clip

    def get_battery_icon_clip(self, charge=0, duration=1.0):
        # fix invalid charge value
        if charge is None:
            charge = 0.0

        # generate the charge string from value
        charge_str = '{:d}%'.format(int(round(charge)))

        # if we have a cache hit, use the cached value
        if charge_str in self.cached_clips['battery']:
            return self.cached_clips['battery'][charge_str]

        # else, create a new clip
        if self.battery_icon_clip is None:
            icon_path = self.compute_battery_icon_path(charge)
            self.battery_icon_clip = (ImageClip(icon_path, duration=duration)
                                      .resize(self.icon_size)
                                      .on_color(col_opacity=0, size=self.resolution, pos='center'))
        else:
            self.battery_icon_clip = self.battery_icon_clip.set_duration(duration)

        # generate a new text to go with the icon
        charge_txt_clip = TextClip(charge_str, fontsize=self.fontsize, font=self.font).set_duration(duration)
        new_icon_clip = self.composite_icon_text(self.battery_icon_clip, charge_txt_clip, self.txt_position)

        # add it to the cache
        self.cached_clips['battery'][charge_str] = new_icon_clip

        # return it
        return new_icon_clip

    def compute_battery_icon_path(self, charge):
        tier_paths = {
            999: '../data/battery.png',
            100: '../data/battery_100.png',
            90: '../data/battery_90.png',
            80: '../data/battery_80.png',
            60: '../data/battery_60.png',
            50: '../data/battery_50.png',
            30: '../data/battery_30.png',
            20: '../data/battery_20.png',
            -999: '../data/battery.png'
        }
        prev_t = 999
        for t in sorted(tier_paths.keys(), reverse=True):
            if charge > t:
                return tier_paths[prev_t]
            else:
                prev_t = t

    def get_speed_icon_clip(self, speed=0.0, duration=1.0):
        # fix invalid value
        if speed is None:
            speed = 0.0

        # generate the string from value
        speed_str = '{:.1f}'.format(speed)

        # if we have a cache hit, use the cached value
        if speed_str in self.cached_clips['speed']:
            return self.cached_clips['speed'][speed_str]

        # else, create a new clip
        if self.speed_icon_clip is None:
            icon_path = '../data/speed.png'
            self.speed_icon_clip = (ImageClip(icon_path, duration=duration)
                                    .resize(self.icon_size)
                                    .on_color(col_opacity=0, size=self.resolution, pos='center'))
        else:
            self.speed_icon_clip = self.speed_icon_clip.set_duration(duration)

        # generate a new text to go with the icon
        speed_txt_clip = TextClip(speed_str, fontsize=self.fontsize, font=self.font).set_duration(duration)
        new_icon_clip = self.composite_icon_text(self.speed_icon_clip, speed_txt_clip, self.txt_position)

        # add it to the cache
        self.cached_clips['speed'][speed_str] = new_icon_clip

        # return it
        return new_icon_clip

    def get_animated_speed_icon_clip(self, speed=0.0, duration=1.0):
        # fix invalid value
        if speed is None:
            speed = 0.0

        # generate the string from value
        speed_str = '{:.1f}'.format(speed)

        # if we have a cache hit, use the cached value
        if speed_str in self.cached_clips['speed']:
            return self.cached_clips['speed'][speed_str]

        # else, create a new clip
        if self.speed_icon_bg_clip is None:
            bg_path = '../data/speed_bg.png'
            self.speed_icon_bg_clip = (ImageClip(bg_path, duration=duration)
                                       .resize(self.icon_size)
                                       .on_color(col_opacity=0, size=self.resolution, pos='center'))
        else:
            self.speed_icon_bg_clip = self.speed_icon_bg_clip.set_duration(duration)

        if self.speed_icon_pointer_clip is None:
            pointer_path = '../data/speed_pointer.png'
            self.speed_icon_pointer_clip = (ImageClip(pointer_path, duration=duration)
                                            .resize(self.icon_size)
                                            .on_color(col_opacity=0, size=self.resolution, pos='center'))
        else:
            self.speed_icon_pointer_clip = self.speed_icon_pointer_clip.set_duration(duration)

        # figure out how much to turn the speed pointer
        v_max = 30.0   # Km/h
        v_min = 0.0    # Km/h
        t = (speed - v_min) / (v_max - v_min)
        a_max = 90.0   # degrees
        a_min = -90.0  # degrees
        angle = (a_max - a_min) * t + a_min

        final_speed_icon = CompositeVideoClip([self.speed_icon_bg_clip,
                                               self.speed_icon_pointer_clip.rotate(-angle, expand=False,
                                                                                   resample='nearest')])

        # generate text to show speed
        speed_txt_clip = TextClip(speed_str, fontsize=self.fontsize, font=self.font).set_duration(duration)

        # generate text to show unit
        speed_unit_clip = (TextClip(self.unit['speed'], fontsize=self.fontsize / 2, font=self.font)
                           .set_duration(duration))

        # composite text with icon
        new_icon_clip = self.composite_icon_text(final_speed_icon, speed_txt_clip, self.txt_position)
        new_icon_clip = self.composite_icon_text(new_icon_clip, speed_unit_clip, self.unit_position)

        # add it to the cache
        self.cached_clips['speed'][speed_str] = new_icon_clip

        # return it
        return new_icon_clip

    def get_temperature_icon_clip(self, temperature=0.0, duration=1.0):
        # fix invalid value
        if temperature is None:
            temperature = 0.0

        # generate the string from value
        temp_str = '{:d}'.format(int(round(temperature)))

        # if we have a cache hit, use the cached value
        if temp_str in self.cached_clips['temperature']:
            return self.cached_clips['temperature'][temp_str]

        # else, create a new clip
        if self.temp_icon_clip is None:
            icon_path = '../data/temp.png'
            self.temp_icon_clip = (ImageClip(icon_path, duration=duration)
                                   .resize(self.icon_size)
                                   .on_color(col_opacity=0, size=self.resolution, pos='center'))
        else:
            self.temp_icon_clip = self.temp_icon_clip.set_duration(duration)

        # generate a new text to go with the icon
        temp_txt_clip = TextClip(temp_str, fontsize=self.fontsize, font=self.font).set_duration(duration)
        temp_unit_clip = (TextClip(self.unit['temperature'], fontsize=self.fontsize/2, font=self.font)
                          .set_duration(duration))
        new_icon_clip = self.composite_icon_text(self.temp_icon_clip, temp_txt_clip, self.txt_position)
        new_icon_clip = self.composite_icon_text(new_icon_clip, temp_unit_clip, self.unit_position)

        # add it to the cache
        self.cached_clips['temperature'][temp_str] = new_icon_clip

        # return it
        return new_icon_clip

    def composite_icon_text(self, icon_clip, text_clip, position):
        off_x = text_clip.w / 2.0
        off_y = text_clip.h / 2.0
        txt_pos_in_px = (
            icon_clip.w * position[0] - off_x,
            icon_clip.h * position[1] - off_y
        )
        return CompositeVideoClip([icon_clip, text_clip.set_position(txt_pos_in_px)])
