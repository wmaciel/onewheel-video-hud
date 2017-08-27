# -*- coding: utf-8 -*-

from moviepy.editor import *
import csv
import sys

icon_manager = 'icon_manager is not initialized'

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

def res_2_tuple(resolution):
    return (resolution['h'], resolution['w'])

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
"""
Main function
"""
def main(data_path, footage_path):
    skip_rows = 90
    video_seconds = 15
    data = parse_logs(data_path, skip_rows)
    footage_clip_res = (720, 1280)
    info_clip_res = (720, 1280) # half of the video
    info_line_res = (720, 256) # 5 lines
    icon_res = (256, 256) # biggest square possible

    print 'Creating icon manager...'
    global icon_manager
    icon_manager = IconManager(resolution=icon_res)

    print 'Generating Footage Clip...'
    footage_clip = generate_footage_clip(footage_path, footage_clip_res, video_seconds)

    print 'Generating Info Clip...'
    info_clip = generate_info_clip(data, info_clip_res, video_seconds)

    print 'Compositing footage and info clips...'
    clip = clips_array([[footage_clip, info_clip.set_pos('center')]])

    print 'Rendering...'
    #clip.write_videofile("onewheel.MP4", fps=60)
    #clip.resize(0.5).preview(fps=60, audio=False)
    info_clip.resize(0.5).preview(fps=60, audio=False)

"""
Opens and loads the video clip captured by the Go Pro
"""
def generate_footage_clip(file_path, resolution, clip_length):
    return (VideoFileClip(file_path)
            .subclip(t_end=clip_length)
            .rotate(-90)
            .resize(resolution))

"""
Generates the clip that will show the data gathered by the App
"""
def generate_info_clip(data, resolution, clip_length):
    n_info_lines = 5
    info_line_resolution = (resolution[0], resolution[1]/n_info_lines)
    print "Generating {} info lines with resolution {}".format(n_info_lines, info_line_resolution)

    speed_text = generate_info_line_clip(data, info_line_resolution, clip_length, '{:>5.1f} Km/h', 'speed', '../data/speed.png')
    battery_text = generate_info_line_clip(data, info_line_resolution, clip_length, '{:>3d}%', 'battery', '../data/battery.png')
    roll_text = generate_info_line_clip(data, info_line_resolution, clip_length, '{:>5.1f}°', 'roll', '../data/roll.png')
    pitch_text = generate_info_line_clip(data, info_line_resolution, clip_length, '{:>5.1f}°', 'pitch', '../data/pitch.png')
    temp_text = generate_info_line_clip(data, info_line_resolution, clip_length, '{:>5.1f} C', 'motor_temp', '../data/temp.png')

    print 'Compositing lines together...'
    info_text_clip = clips_array([
        [speed_text],
        [pitch_text],
        [roll_text],
        [battery_text],
        [temp_text]
    ])

    bg_clip = TextClip(' ', size=resolution, bg_color='white').set_duration(clip_length)
    info_text_clip = CompositeVideoClip([bg_clip, info_text_clip])

    return info_text_clip

def generate_info_line_clip(data,  resolution, clip_length, text, column_name, icon_path):
    print 'Generating {} info line clip. {}'.format(column_name, resolution)
    info_clips = []
    global icon_manager
    icon_resolution=(resolution[1], resolution[1])
    for i in range(clip_length):
        data_str = data[i][column_name]
        icon_clip = {
            'pitch': icon_manager.get_pitch_icon_clip(angle=float(data_str)),
            'roll': icon_manager.get_roll_icon_clip(angle=float(data_str)),
            'speed': icon_manager.get_speed_icon_clip(),
            'battery': icon_manager.get_battery_icon_clip(),
            'motor_temp': icon_manager.get_temperature_icon_clip()
        }[column_name]

        txt_resolution = (resolution[0] - icon_resolution[0], resolution[1])
        txt_clip = generate_info_text_clip(text.format(data_str), txt_resolution, 1, 100)

        txt_icon_clip = clips_array([[icon_clip, txt_clip.set_pos("center")]])
        info_clips.append(txt_icon_clip)

    line_clip = concatenate_videoclips(info_clips)
    return line_clip

def generate_info_text_clip(text, resolution, clip_length, padding):
    txt_clip = (TextClip(text, fontsize=70, color='blue', font='Consolas')
                .set_duration(clip_length)
                .on_color(col_opacity=0, size=resolution, pos=('left', 'center')))
    return txt_clip

"""
Converts Miles to Kilometers
"""
def mile2Km(mile):
    return float(mile) * 1.609344

"""
Converts from Farenheint to Celsius
"""
def f_to_c(f_temp):
    try:
        return (float(f_temp) - 32) * 5.0 / 9.0
    except ValueError:
        return None

"""
Converts the original angle to values between -180 and 180, with 0 being horizontal
"""
def parse_angle(angle_text):
    try:
        return float(angle_text)/10 - 180
    except ValueError:
        return None

"""
Parses the log files and creates a list of dicts
"""
def parse_logs(file_path, skip_rows=0):
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

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Wrong number of arguments.'
        print 'Usage: python test.py <data_path> <footage_path>'
        exit(1)

    onewheel_video = OnewheelHudVideo(sys.argv[1], sys.argv[2], length=20)
    onewheel_video.render()

    #main(sys.argv[1], sys.argv[2])
