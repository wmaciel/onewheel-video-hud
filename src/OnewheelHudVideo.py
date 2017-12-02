# -*- coding: utf-8 -*-
from datetime import timedelta
import tqdm
from moviepy.editor import *
from IconManager import IconManager
import LogParser

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
    def __init__(self, data_path, footage_path, orientation='portrait', resolution='1080', start_second=0,
                 start_date=None, end_second=None, unit='mm'):
        self.footage_path = footage_path
        self.orientation = orientation
        self.resolutions = compute_resolutions(orientation, resolution)
        self.start_second = start_second
        self.end_second = end_second
        self.icon_manager = IconManager(resolution=res_2_tuple(self.resolutions['icon']))
        self.data = LogParser.parse(data_path, unit)
        self.start_date = LogParser.parse_millisecond_time(start_date)

        print 'Footage is coming from', self.footage_path
        print 'Footage orientation is', self.orientation
        print 'Resolutions are:'
        print self.resolutions

    def render(self):
        print 'Generating footage clip...'
        footage_clip = self.generate_footage_clip()

        print 'Generating info clip...'
        info_clip = self.generate_fps_info_clip(footage_clip, self.start_date)

        print 'Generating final clip...'
        final_clip = CompositeVideoClip([footage_clip, info_clip.set_position('bottom', 'center')])

        print 'Rendering...'
        final_clip.write_videofile("onewheel.MP4", fps=60, threads=8)
        # final_clip.preview(fps=60, audio=False)
        # final_clip.save_frame(filename="frame.png", t=10.669)

    def generate_fps_info_clip(self, footage, start_date):
        icon_clips = {
            'speed': [],
            'pitch': [],
            'roll': [],
            'battery': [],
            'temperature': []
        }

        frame_duration = 1.0/footage.fps
        last_id = 0
        for t in tqdm.tqdm(f_range(0, footage.duration, frame_duration)):
            row, last_id = interpolate_from_data(self.data, timedelta(seconds=t), start_date, last_id)

            icon_clips['speed'].append(self.icon_manager.get_speed_icon_clip(speed=row['speed'],
                                                                             duration=frame_duration))
            icon_clips['pitch'].append(self.icon_manager.get_pitch_icon_clip(angle=row['pitch'],
                                                                             duration=frame_duration))
            icon_clips['roll'].append(self.icon_manager.get_roll_icon_clip(angle=row['roll'],
                                                                           duration=frame_duration))
            icon_clips['battery'].append(self.icon_manager.get_battery_icon_clip(charge=row['battery'],
                                                                                 duration=frame_duration))
            icon_clips['temperature'].append(self.icon_manager.get_temperature_icon_clip(temperature=row['motor_temp'],
                                                                                         duration=frame_duration))
        print 'Combining icons...'
        info_clip = self.combine_info_clips(icon_clips)
        return info_clip

    def compute_log_delay(self, i):
        delta_t = self.data[i + 1]['time'] - self.data[i]['time']
        delta_seconds = delta_t.seconds + delta_t.microseconds * 1e-6
        return delta_seconds

    def generate_time_clip(self):
        time_clips = []
        for row in tqdm.tqdm(self.data[:300]):
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
            raise Exception("Orientation not set")

    def generate_footage_clip(self):
        footage_clip = (VideoFileClip(self.footage_path)
                        .resize(res_2_tuple(self.resolutions['footage'])))

        footage_clip = footage_clip.subclip(t_start=self.start_second, t_end=self.end_second)

        if self.orientation == 'portrait':
            footage_clip = footage_clip.rotate(-90)

        return footage_clip


def compute_resolutions(orientation, resolution_name):
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
    # in landscape, the icons will be laid along the right edge
    else:  # orientation == landscape
        resolutions['icon'] = {
            'w': resolution['h'] / float(n_icons),
            'h': resolution['h'] / float(n_icons)
        }

    return resolutions


def interpolate_from_data(data, delta_t, start_date, last_id=0):
    # find between which rows is t in
    t = delta_t + start_date
    id_1 = None
    id_2 = None
    for i, row in enumerate(data[last_id:]):
        if row['time'] >= t:
            id_2 = i + last_id
            id_1 = id_2 - 1
            break

    # find interpolation offset x
    d1 = data[id_1]['time']
    d2 = data[id_2]['time']
    x = (t - d1).total_seconds() / (d2 - d1).total_seconds()

    # use x offset to interpolate attributes
    row = {'time': t}
    r1 = data[id_1]
    r2 = data[id_2]
    for item in r1.items():
        if item[0] != 'time':
            a1 = r1[item[0]]
            a2 = r2[item[0]]
            if a1 is None or a2 is None:
                row[item[0]] = None
            else:
                row[item[0]] = (a2 - a1) * x + a1

    return row, id_2


def compute_average_delta_t(data):
    deltas_s = []

    for i, row in enumerate(data):
        if i + 1 < len(data):
            delta_t = data[i + 1]['time'] - row['time']
            deltas_s.append(round(delta_t.seconds + delta_t.microseconds * 1e-6, 2))

    return sum(deltas_s) / len(deltas_s)


def res_2_tuple(resolution):
    """
    Converts a resolution map to a tuple
    """
    return resolution['h'], resolution['w']


def f_range(start, stop, step):
    """"
    Implementation of the range built-in range function using floating point numbers as shown at:
    https://www.pythoncentral.io/pythons-range-function-explained/
    """
    i = start
    while i < stop:
        yield i
        i += step


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generates a HUD video of your onewheel ride from a log file')
    parser.add_argument('log_file', type=str, help='Path to the logfile used to annotate the video')
    parser.add_argument('video_file', type=str, help='Path to the video to be annotated')
    parser.add_argument('--start-second', type=float, default=0, help='Which second of the original footage should the '
                                                                      'final video start from')
    parser.add_argument('--start-date', type=str, default='0', help='Timestamp at the moment of the frame on '
                                                                    'start_second')
    parser.add_argument('--end-second', type=float, default=None, help='Which second of the original footage the the '
                                                                       'final video end at')
    parser.add_argument('--unit', type=str, default='mm', choices=['mm', 'mi', 'im', 'ii'],
                        help='Defines input output unit conversion with two letters. The first denotes the input unit '
                             'and the second denotes the output unit.')
    args = parser.parse_args()
    onewheel_video = OnewheelHudVideo(args.log_file,
                                      args.video_file,
                                      start_second=args.start_second,
                                      start_date=args.start_date,
                                      end_second=args.end_second,
                                      unit=args.unit)
    onewheel_video.render()
