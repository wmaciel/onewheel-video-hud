from moviepy.editor import *
import csv

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
    #clip = CompositeVideoClip([clip, counting_clip.set_pos('center')])
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
    bg_clip = ImageClip("black.jpg", duration=clip_length)
    speed_clip = generate_speed_clip(data, skip_rows, clip_length)
    return CompositeVideoClip([bg_clip, speed_clip])

def generate_speed_clip(data, skip_rows, clip_length):
    speed_clips = []
    for i in range(skip_rows, clip_length + skip_rows):
        speed_text = '{: 4.1f} Km/h'.format(mile2Km(data[i]['speed']))
        print speed_text
        txt_clip = TextClip(speed_text, fontsize=70, color='red').set_duration(1)
        speed_clips.append(txt_clip)
    speed_clip = concatenate_videoclips(speed_clips)
    return speed_clip

"""
Converts Miles to Kilometers
"""
def mile2Km(mile):
    return float(mile) * 1.609344

"""
Parses the log files and creates a list of dicts
"""
def parse_logs(file_path):
    print 'Loading log file ', file_path, '...'
    data = []
    with open(file_path) as logfile:
        log_reader = csv.reader(logfile, delimiter=',')
        for row in log_reader:
            data.append({
                'time':row[0],
                'speed':row[1]
                })
    print 'Loaded ', len(data), 'rows'
    return data

if __name__ == '__main__':
    if len(sys.argv) != 3
        print 'Wrong number of arguments.'
        print 'Usage: python test.py <data_path> <footage_path>'
        exit(1)

    main(sys.argv[1], sys.argv[2])
