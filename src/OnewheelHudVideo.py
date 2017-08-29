# -*- coding: utf-8 -*-
from moviepy.editor import *
from IconManager import IconManager
import csv
from datetime import datetime

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
    def __init__(self, data_path, footage_path, orientation='portrait', resolution='1080', start_second=0, skip_rows=0, length=None):
        self.footage_path = footage_path
        self.orientation = orientation
        self.resolutions = self.compute_resolutions(orientation, resolution)
        self.length = length
        self.icon_manager = IconManager(resolution=res_2_tuple(self.resolutions['icon']))
        self.data = parse_logs(data_path, skip_rows=skip_rows)
        self.avg_log_delay = compute_average_delta_t(self.data)

        print 'Footage is comming from', self.footage_path
        print 'Footage orientation is', self.orientation
        print 'Resolutions are:'
        print self.resolutions
        print 'Logging delay is {} seconds'.format(self.avg_log_delay)

    def render(self):
        print 'Generating footage clip...'
        footage_clip = self.generate_footage_clip().subclip(t_start=start_second)
        print 'Generating info clip...'
        info_clip = self.generate_info_clip()
        #print 'Generating time clip...'
        #time_clip = self.generate_time_clip()
        print 'Generating final clip...'
        final_clip = CompositeVideoClip([footage_clip, info_clip.set_position('bottom', 'center')])
        #final_clip = CompositeVideoClip([footage_clip, info_clip.set_position('bottom', 'center'), time_clip.set_position('top', 'center')])
        print 'Rendering...'
        #final_clip.save_frame('frame.png', t=0)
        #final_clip.resize(0.4).preview(fps=60, audio=False)
        final_clip.write_videofile("onewheel.MP4", fps=60, threads=8)
        #info_clip.preview(fps=60, audio=False)

    def generate_info_clip(self):
        icon_clips = {
            'speed': [],
            'pitch': [],
            'roll': [],
            'battery': [],
            'temperature': []
        }

        print 'Getting icons...'
        for i, row in enumerate(self.data):
            print "{:>0.2f}%".format(100.0 * float(i+1) / len(self.data))
            delta_seconds = self.avg_log_delay
            icon_clips['speed'].append(self.icon_manager.get_speed_icon_clip(speed=row['speed'], duration=delta_seconds))
            icon_clips['pitch'].append(self.icon_manager.get_pitch_icon_clip(angle=row['pitch'], duration=delta_seconds))
            icon_clips['roll'].append(self.icon_manager.get_roll_icon_clip(angle=row['roll'], duration=delta_seconds))
            icon_clips['battery'].append(self.icon_manager.get_battery_icon_clip(charge=row['battery'], duration=delta_seconds))
            icon_clips['temperature'].append(self.icon_manager.get_temperature_icon_clip(temperature=row['motor_temp'], duration=delta_seconds))
        print 'Combining icons...'
        info_clip = self.combine_info_clips(icon_clips)
        return info_clip

    def generate_time_clip(self):
        time_clips = []
        for row in self.data:
            time_str = '{}'.format(row['time'])
            time_clips.append(TextClip(time_str, fontsize=64, color='red').set_duration(self.avg_log_delay))
        return concatenate_videoclips(time_clips)

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
                'time':parse_milisecond_time(row['time']),
                'speed':mile2Km(row['speed']),
                'battery':int(row['battery']),
                'roll':parse_angle(row['tilt_angle_roll']),
                'pitch':parse_angle(row['tilt_angle_pitch']),
                'motor_temp':f_to_c(row['motor_temp'])
                })
    print 'Loaded ', len(data), 'rows'
    return data[skip_rows:]

def compute_average_delta_t(data):
    deltas_s = []

    for i, row in enumerate(data):
        if i+1 < len(data):
            delta_t = data[i+1]['time'] - row['time']
            deltas_s.append(round(delta_t.seconds + delta_t.microseconds * 1e-6, 2))

    return sum(deltas_s)/len(deltas_s)

def parse_original_time(time_str):
    # remove timezone info
    time_str = time_str[:-5]
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

def parse_milisecond_time(time_str): # "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
    # remove timezone info
    time_str = time_str[:-5]
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

def res_2_tuple(resolution):
    """
    Converts a resolution map to a tuple
    """
    return (resolution['h'], resolution['w'])
