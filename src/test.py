from moviepy.editor import *
import csv
import sys

"""
Main function
"""
def main(data_path, footage_path):
    data = parse_logs(data_path)
    skip_rows = 90
    video_seconds = 15

    print 'Generating Footage Clip...',
    footage_clip = generate_footage_clip(footage_path, video_seconds)
    print 'OK'

    print 'Generating Info Clip...',
    info_clip = generate_info_clip(data, skip_rows, video_seconds)
    print 'OK'

    print 'Compositing...',
    #clip = clips_array([[footage_clip, info_clip.set_pos('center')]])
    print 'OK'

    print 'Rendering...'
    #clip.write_videofile("onewheel.MP4", fps=60)
    #clip.preview(fps=60, audio=False)
    info_clip.preview(fps=60, audio=False)
    print 'OK'

"""
Opens and loads the video clip captured by the Go Pro
"""
def generate_footage_clip(file_path, clip_length):
    return VideoFileClip(file_path).subclip(t_end=clip_length).rotate(-90)

"""
Generates the clip that will show the data gathered by the App
"""
def generate_info_clip(data, skip_rows, clip_length):
    bg_clip = ImageClip("../data/black.jpg", duration=clip_length)
    speed_clip = generate_info_text_clip(data, skip_rows, clip_length)
    return CompositeVideoClip([bg_clip, speed_clip])

def generate_info_text_clip(data, skip_rows, clip_length):
    speed_text = generate_info_line_clip(data, skip_rows, clip_length, 'Speed: {: 4.1f} Km/h', 'speed')
    battery_text = generate_info_line_clip(data, skip_rows, clip_length, 'Battery: {}%', 'battery')
    roll_text = generate_info_line_clip(data, skip_rows, clip_length, 'Roll: {}', 'roll')
    pitch_text = generate_info_line_clip(data, skip_rows, clip_length, 'Pitch: {}', 'pitch')
    temp_text = generate_info_line_clip(data, skip_rows, clip_length, 'Temp: {} C', 'motor_temp')
    info_text_clip = clips_array([
        [speed_text],
        [pitch_text],
        [roll_text],
        [battery_text],
        [temp_text]
    ])
    return info_text_clip


def generate_info_line_clip(data, skip_rows, clip_length, text, column_name):
    info_clips = []
    for i in range(skip_rows, clip_length + skip_rows):
        txt_clip = TextClip(text.format(data[i][column_name]), fontsize=50, color='red').set_duration(1)
        info_clips.append(txt_clip)
    line_clip = concatenate_videoclips(info_clips)
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
def parse_logs(file_path):
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
    return data

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Wrong number of arguments.'
        print 'Usage: python test.py <data_path> <footage_path>'
        exit(1)

    main(sys.argv[1], sys.argv[2])
