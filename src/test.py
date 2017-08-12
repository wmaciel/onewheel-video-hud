from moviepy.editor import *
import csv
import sys

"""
Main function
"""
def main(data_path, footage_path):
    skip_rows = 90
    video_seconds = 15
    data = parse_logs(data_path, skip_rows)
    footage_clip_res = (720, 1280)
    info_clip_res = (720, 128)

    print 'Generating Footage Clip...'
    footage_clip = generate_footage_clip(footage_path, footage_clip_res, video_seconds)

    print 'Generating Info Clip...'
    info_clip = generate_info_clip(data, video_seconds)

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
    speed_clip = generate_info_text_clip(data, resolution, clip_length)
    return speed_clip

def generate_info_text_clip(data, resolution, clip_length):
    speed_text = generate_info_line_clip(data, resolution, clip_length, '{: > 4.1f} Km/h', 'speed', '../data/speed.png')
    battery_text = generate_info_line_clip(data, resolution, clip_length, '{: > 4d}%', 'battery', '../data/battery.png')
    roll_text = generate_info_line_clip(data, resolution, clip_length, '{: > 4.1f}', 'roll', '../data/roll.png')
    pitch_text = generate_info_line_clip(data, resolution, clip_length, '{: > 4.1f}', 'pitch', '../data/pitch.png')
    temp_text = generate_info_line_clip(data, resolution, clip_length, '{: > 4.1f} C', 'motor_temp', '../data/temp.png')
    
    print 'Compositing lines together...'
    info_text_clip = CompositeVideoClip([
        speed_text.on_color(color=[255,255,255], size=(720,1280), pos=('left', 'top')),
        pitch_text.set_position((0.0, 0.2), relative=True),
        roll_text.set_position((0.0, 0.4), relative=True),
        battery_text.set_position((0.0, 0.6), relative=True),
        temp_text.set_position((0.0, 0.8), relative=True)
    ])

    return info_text_clip


def generate_info_line_clip(data,  resolution, clip_length, text, column_name, icon_path):
    print 'Generating {} line clip...'.format(column_name)
    info_clips = []
    for i in range(clip_length):
        txt_clip = TextClip(text.format(data[i][column_name]), fontsize=70, color='black').set_duration(1)
        icon_clip = ImageClip(icon_path, duration=1).resize(.9)
        txt_icon_clip = clips_array([[icon_clip, txt_clip.set_pos("center")]])
        info_clips.append(txt_icon_clip)
    line_clip = concatenate_videoclips(info_clips)
    new_size = (line_clip.size[0] + 20, line_clip.size[1] + 20)
    line_clip = line_clip.on_color(col_opacity=0.0, size=new_size)
    return line_clip

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
def parse_logs(file_path, skip_rows):
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

    main(sys.argv[1], sys.argv[2])
