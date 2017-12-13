# onewheel-video-hud
Places a Heads Up Display on your Onewheel video based on the log file created by the [pOneWheel] app

As it stands now, this script can show speed, pitch and roll angle, motor temperature and battery charge

## Example
This is a sample of what this script will output

[![Video link](https://img.youtube.com/vi/yXMGHKQnptA/hqdefault.jpg)](https://youtu.be/yXMGHKQnptA)

## How to use
The script contains a help output which should be able to explain all the parameters it takes.
Keep in mind that the script must be executed from the same directory it is in, as it depends on the relative path to the images to work.

```
python OneWheelHud.py -h

usage: OnewheelHudVideo.py [-h] [--start-second START_SECOND]
                           [--start-date START_DATE] [--end-second END_SECOND]
                           [--unit {mm,mi,im,ii}] [--output-file OUTPUT_FILE]
                           log_file video_file

Generates a HUD video of your onewheel ride from a log file

positional arguments:
  log_file              Path to the logfile used to annotate the video
  video_file            Path to the video to be annotated

optional arguments:
  -h, --help            show this help message and exit
  --start-second START_SECOND
                        Which second of the original footage should the final
                        video start from
  --start-date START_DATE
                        Timestamp at the moment of the frame on start_second
  --end-second END_SECOND
                        Which second of the original footage the the final
                        video end at
  --unit {mm,mi,im,ii}  Defines input output unit conversion with two letters.
                        The first denotes the input unit and the second
                        denotes the output unit.
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Path the output file. If none is given a file called
                        onewheel.MP4 will be created on the directory the
                        script if being run.
```

[pOneWheel]:(https://github.com/ponewheel/android-ponewheel)