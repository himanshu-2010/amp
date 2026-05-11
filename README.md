# AMP - Ascii Media Player

A terminal-based ASCII media player that visualizes videos, images, GIFs, and streams as ASCII art directly in your terminal.

![AMP Screenshot](https://via.placeholder.com/800x400?text=AMP+ASCII+Media+Player)

## Features

- **Multiple Format Support**: Videos, images, GIFs, webcams, and streams
- **Streaming Protocols**: RTSP, RTMP, UDP, SRT, HTTP/HTTPS
- **10 Charset Options**: Including emoji support
- **Playback Controls**: Loop, smooth scaling, grayscale, stretch
- **File Browser**: Navigate and play media files directly
- **Customizable**: Multiple rendering options and effects
- **Sound Support**: Audio playback via tplay backend

## Installation

### Quick Install

```bash
./install.sh
```

The installer will:
1. Detect your operating system
2. Install required dependencies (ffmpeg, python3, etc.)
3. Install tplay via cargo
4. Create a global `amp` command

### Manual Installation

1. Install dependencies:
   - **FFmpeg** (with dev libraries)
   - **Python 3.8+**
   - **Cargo** (for tplay)
   - **ncurses** development files

2. Install tplay:
   ```bash
   cargo install tplay
   ```

3. Make amp executable:
   ```bash
   chmod +x amp.py
   ```

4. Create a symlink (optional):
   ```bash
   sudo ln -s $(pwd)/amp.py /usr/local/bin/amp
   ```

## Usage

### Basic Usage

```bash
amp                     # Start file browser at home directory
amp /path/to/media      # Start file browser at specific directory
amp video.mp4           # Play video directly
amp image.png          # Display image directly
amp https://...         # Play from URL/stream
```

### Controls

**File Browser:**
| Key | Action |
|-----|--------|
| ↑/↓ | Navigate files |
| Enter/Space | Play selected file |
| B | Stop playback |
| U | Enter URL/stream |
| 1-0 | Change charset |
| G | Toggle grayscale |
| N | Toggle newlines |
| A | Toggle auto-exit |
| F | Toggle frame skip |
| W | Toggle wide mode |
| S | Toggle smooth scaling |
| T | Toggle stretch |
| L | Toggle loop |
| +/- | Adjust FPS |
| ? | Toggle help |
| Q | Quit |

**During Playback (tplay controls):**
| Key | Action |
|-----|--------|
| Space | Pause/unpause |
| g | Toggle grayscale/color |
| m | Toggle mute/unmute |
| ←/→ | Seek 5 seconds |
| j/l | Seek 10 seconds |
| [ / ] | Adjust speed ±0.25x |
| , / . | Adjust speed ±0.1x |
| \ | Reset speed to 1x |
| c/C | Subtitle controls |
| q | Quit |

## Examples

```bash
# Play local video
amp ./video.mp4

# Play local image
amp ./image.png

# Play YouTube video
amp https://www.youtube.com/watch?v=...

# Play with emoji charset
amp video.mp4
# Then press '9' or '0' for emoji mode

# Play RTSP stream (IP camera)
amp rtsp://192.168.1.100:554/live

# Play UDP stream
amp udp://239.0.0.1:1234

# Play webcam
amp /dev/video0
```

## Charset Options

| Key | Description |
|-----|-------------|
| 1 | Basic (10 chars) |
| 2 | Detailed (67 chars) |
| 3 | Ultra (92 chars) - Default |
| 4 | Block gradient |
| 5 | Solid block |
| 6 | Dotted |
| 7 | Black/White |
| 8 | B/W Dotted |
| 9 | Moon emoji 🌑🌒🌓🌔🌕🌖🌗🌘 |
| 0 | Fruit emoji 🍎🍏🍐🍊🍋🍌🍍🍎 |

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.

**You CANNOT sell this software or include it in commercial products.**

See [LICENSE](LICENSE) for full details.

## Requirements

- Python 3.8+
- FFmpeg
- Cargo (for tplay)
- A terminal with 256+ color support

## Troubleshooting

### Terminal display issues
- Make sure your terminal supports 256 colors
- Try adjusting terminal size

### Audio not working
- Ensure audio device is available
- Check volume settings

### YouTube videos not playing
- Some videos may be blocked due to age restrictions or region locks
- Try different videos or use local files

## Acknowledgments

- [tplay](https://github.com/maxcurzi/tplay) - The backend ASCII renderer
- FFmpeg - Media processing