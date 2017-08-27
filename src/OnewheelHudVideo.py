# -*- coding: utf-8 -*-
from moviepy.editor import *
from IconManager import IconManager
import csv

resolution_map = {
    '1080': {
        'portrait': {'w': 1080, 'h': 1920},
        'landscape': {'w': 1920, 'h': 1080}
    },
    '720': {
        'portrait': {'w': 720, 'h': 1280},
        'landscape': {'w': 1280, 'h': 720}
    }
}

class OnewheelHudVideo:
    def __init__(self, data_path, footage_path, orientation='portrait', resolution='1080', length=None):
        self.data_path = data_path
        self.footage_path = footage_path
        self.orientation = orientation
        self.resolutions = self.compute_resolutions(orientation, resolution)
        self.length = length
        self.icon_manager = IconManager(resolution=res_2_tuple(self.resolutions['icon']))
        self.data = parse_logs(data_path)

        print 'Data is comming from', self.data_path
        print 'Footage is comming from', self.footage_path
        print 'Footage orientation is', self.orientation
        print 'Resolutions are:'
        print self.resolutions

    def render(self):
        print 'Generating footage clip...'
        footage_clip = self.generate_footage_clip()
        print 'Generating info clip...'
        info_clip = self.generate_info_clip()
        print 'Generating final clip...'
        final_clip = CompositeVideoClip([footage_clip, info_clip.set_position('bottom', 'center')])
        print 'Rendering...'
        final_clip.resize(0.5).preview(fps=60, audio=False)

    def generate_info_clip(self):
        icon_clips = {
            'speed': [],
            'pitch': [],
            'roll': [],
            'battery': [],
            'temperature': []
        }

        for row in self.data:
            icon_clips['speed'].append(self.icon_manager.get_speed_icon_clip())
            icon_clips['pitch'].append(self.icon_manager.get_pitch_icon_clip())
            icon_clips['roll'].append(self.icon_manager.get_roll_icon_clip())
            icon_clips['battery'].append(self.icon_manager.get_battery_icon_clip())
            icon_clips['temperature'].append(self.icon_manager.get_temperature_icon_clip())

        info_clip = self.combine_info_clips(icon_clips)
        return info_clip

    def combine_info_clips(self, icon_clips):
        # combine clips by info
        full_icon_clips = [
            concatenate_videoclips(icon_clips['speed']),
            concatenate_videoclips(icon_clips['pitch']),
            concatenate_videoclips(icon_clips['roll']),
            concatenate_videoclips(icon_clips['battery']),
            concatenate_videoclips(icon_clips['temperature'])
        ]

        # combine info clips into a bar
        if self.orientation == 'portrait':
            # make a horizontal bar
            return clips_array([full_icon_clips])
        elif self.orientation == 'landscape':
            # transpose full_icon_clips
            vertical_array = [
                [full_icon_clips[0]],
                [full_icon_clips[1]],
                [full_icon_clips[2]],
                [full_icon_clips[3]],
                [full_icon_clips[4]]
            ]
            # make a vertical bar
            return clips_array(vertical_array)
        else:
            raise Exception ("Orientation not set")


    def generate_footage_clip(self):
        footage_clip = (VideoFileClip(self.footage_path)
            .resize(res_2_tuple(self.resolutions['footage'])))

        if self.length is not None:
            footage_clip = footage_clip.subclip(t_end=self.length)

        if self.orientation == 'portrait':
            footage_clip = footage_clip.rotate(-90)

        return footage_clip

    def compute_resolutions(self, orientation, resolution_name):
        resolution = resolution_map[resolution_name][orientation]
        resolutions = {}
        n_icons = 5

        # the footage is the same as the full resolution
        resolutions['footage'] = resolution

        # in portrait, the icons will be layed along the bottom edge
        if orientation == 'portrait':
            resolutions['icon'] = {
                'w': resolution['w'] / float(n_icons),
                'h': resolution['w'] / float(n_icons)
            }
        # in landscape, the icons will be layed along the right edge
        else: # orientation == landscape
            resolutions['icon'] = {
                'w': resolution['h'] / float(n_icons),
                'h': resolution['h'] / float(n_icons)
            }

        return resolutions

def mile2Km(mile):
    """
    Converts Miles to Kilometers
    """
    return float(mile) * 1.609344


def f_to_c(f_temp):
    """
    Converts from Farenheint to Celsius
    """
    try:
        return (float(f_temp) - 32) * 5.0 / 9.0
    except ValueError:
        return None

def parse_angle(angle_text):
    """
    Converts the original angle to values between -180 and 180, with 0 being horizontal
    """
    try:
        return float(angle_text)/10 - 180
    except ValueError:
        return None

def parse_logs(file_path, skip_rows=0):
    """
    Parses the log files and creates a list of dicts
    """
    print 'Loading log file ', file_path, '...'
    data = []
    with open(file_path) as logfile:
        log_reader = csv.DictReader(logfile)
        for row in log_reader:
            data.append({
                'time':row['time'],
                'speed':mile2Km(row['speed']),
                'battery':int(row['battery']),
                'roll':parse_angle(row['tilt_angle_roll']),
                'pitch':parse_angle(row['tilt_angle_pitch']),
                'motor_temp':f_to_c(row['motor_temp'])
                })
    print 'Loaded ', len(data), 'rows'
    return data[skip_rows:]

def res_2_tuple(resolution):
    """
    Converts a resolution map to a tuple
    """
    return (resolution['h'], resolution['w'])
