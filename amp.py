#!/usr/bin/env python3
"""
AMP - Ascii Media Player
"""

import subprocess
import os
import sys
import curses
import curses.textpad
import time
import threading
import argparse
from pathlib import Path

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.m4v', '.ts', '.gif'}
AUDIO_EXTS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.opus', '.wma'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

STREAM_PROTOCOLS = {'rtsp://', 'rtmp://', 'udp://', 'srt://', 'http://', 'https://', 'mms://', 'mmst://'}
DEVICE_PATHS = {'/dev/video', '/dev/video0', '/dev/video1', '/dev/video2'}

def is_playable(path):
    p = str(path).lower()
    if p.startswith(('rtsp://', 'rtmp://', 'udp://', 'srt://', 'http://', 'https://', 'mms://', 'mmst://')):
        return True
    if p.startswith('/dev/video'):
        return True
    return Path(p).suffix in VIDEO_EXTS | IMAGE_EXTS | AUDIO_EXTS

CHAR_MAPS = {
    '1': ' .:-=+*#%@',          # CHARS1 (10 chars)
    '2': " .'`^\",:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",  # CHARS2 (67 chars)
    '3': " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@",  # CHARS3 default (92 chars)
    '4': ' ░▒▓█',               # GRADIENT (5 chars)
    '5': '█',                  # SOLID
    '6': '⣿',                  # DOTTED
    '7': ' █',                  # BLACKWHITE
    '8': ' ⣿',                  # BW_DOTTED
    '9': '🌑🌒🌓🌔🌕🌖🌗🌘',  # Moon emoji
    '0': '🍎🍏🍐🍊🍋🍌🍍🍎',  # Fruit emoji
}

class FileManager:
    def __init__(self, start_path=None):
        self.path = Path(start_path or os.path.expanduser('~'))
        self.entries = []
        self.selected_idx = 0
        self.scroll_offset = 0
        self.hidden = False
        self.reload()
    
    def reload(self):
        try:
            items = []
            for e in os.listdir(self.path):
                if not e.startswith('.') or self.hidden:
                    p = self.path / e
                    items.append((e, p.is_dir()))
            items.sort(key=lambda x: (not x[1], x[0].lower()))
            self.entries = items
            self.selected_idx = min(self.selected_idx, max(0, len(self.entries) - 1))
        except:
            self.entries = []
    
    @property
    def selected_entry(self):
        if 0 <= self.selected_idx < len(self.entries):
            return self.path / self.entries[self.selected_idx][0]
        return None
    
    def move_up(self):
        self.selected_idx = max(0, self.selected_idx - 1)
    
    def move_down(self):
        self.selected_idx = min(len(self.entries) - 1, self.selected_idx + 1)
    
    def open_selected(self):
        if self.selected_entry and self.selected_entry.is_dir():
            self.path = self.selected_entry
            self.selected_idx = 0
            self.reload()
            return None
        elif self.selected_entry and self.selected_entry.is_file():
            return self.selected_entry
        return None
    
    def go_parent(self):
        if self.path.parent != self.path:
            self.path = self.path.parent
            self.selected_idx = 0
            self.reload()
    
    def get_display(self, name):
        p = self.path / name
        if p.is_dir():
            return ('📁', name)
        ext = p.suffix.lower()
        if ext in VIDEO_EXTS:
            return ('🎬', name)
        elif ext in AUDIO_EXTS:
            return ('🎵', name)
        elif ext in IMAGE_EXTS:
            return ('🖼️', name)
        return ('📄', name)
    
    def update_scroll(self, visible):
        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + visible:
            self.scroll_offset = self.selected_idx - visible + 1


class TPlayPlayer:
    def __init__(self):
        self.process = None
        self.running = False
    
    def play(self, filepath, char_map=' ░▒▓█', loop=False, smooth=False, fps=30, gray=False, stretch=False, auto_exit=False, new_lines=False, frame_skip=False, w_mod=1):
        self.stop()
        
        cmd = ['tplay', str(filepath), '--char-map', char_map, '--fps', str(fps)]
        if loop:
            cmd.append('--loop-playback')
        if smooth:
            cmd.append('--smooth')
        if gray:
            cmd.append('--gray')
        if stretch:
            cmd.append('--stretch')
        if auto_exit:
            cmd.append('--auto-exit')
        if new_lines:
            cmd.append('--new-lines')
        if frame_skip:
            cmd.append('--allow-frame-skip')
        if w_mod > 1:
            cmd.extend(['--w-mod', str(w_mod)])
        
        self.process = subprocess.Popen(cmd)
        self.running = True
    
    def stop(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1)
            except:
                self.process.kill()
            self.process = None
        self.running = False
        # Restore terminal after tplay exits
        os.system('clear 2>/dev/null')
        sys.stdout.write("\033[?1049l\033[?25h\033[0m\033[2J\033[H")
        sys.stdout.flush()
    
    def is_running(self):
        return self.running and self.process and self.process.poll() is None


class TPlayApp:
    def __init__(self, start_path):
        self.fm = FileManager(start_path)
        self.player = TPlayPlayer()
        self.char_map = ' ░▒▓█'
        self.loop = False
        self.smooth = False
        self.gray = False
        self.stretch = False
        self.auto_exit = False
        self.new_lines = False
        self.frame_skip = False
        self.w_mod = 1
        self.fps = 30
        self.playing = False
        self.current_file = None
        self.show_help = False
    
    def _cleanup_terminal(self):
        os.system('clear 2>/dev/null')
        sys.stdout.write("\033[?1049l\033[?25h\033[0m\033[2J\033[H")
        sys.stdout.flush()
    
    def run(self):
        os.environ.setdefault('ESCDELAY', '25')
        try:
            curses.wrapper(self._main)
        finally:
            self.player.stop()
            self._cleanup_terminal()
    
    def _main(self, stdscr):
        curses.curs_set(0)
        
        while True:
            h, w = stdscr.getmaxyx()
            stdscr.erase()
            
            if self.playing and self.player.is_running():
                self._draw_player(stdscr, h, w)
            else:
                if self.playing and not self.player.is_running():
                    self.playing = False
                self._draw_browser(stdscr, h, w)
            
            try:
                stdscr.timeout(50)
                key = stdscr.getch()
            except:
                key = -1
            
            if key == ord('q'):
                break
            elif key == ord('h') or key == ord('H'):
                self.show_help = not self.show_help
            
            if self.playing and self.player.is_running():
                self._handle_player_key(key)
            else:
                self._handle_browser_key(key, stdscr, h)
            
            time.sleep(0.02)
        
        # Restore terminal on exit
        sys.stdout.write("\033[?1049l")
        sys.stdout.write("\033[?25h")
        sys.stdout.write("\033[0m")
        sys.stdout.flush()
    
    def _draw_browser(self, stdscr, h, w):
        title = f" AMP Browser - {self.fm.path} ".ljust(w)
        stdscr.addstr(0, 0, title, curses.A_REVERSE | curses.A_BOLD)
        
        visible = h - 4
        self.fm.update_scroll(visible)
        
        for i in range(visible):
            idx = i + self.fm.scroll_offset
            if idx >= len(self.fm.entries):
                break
            
            name, is_dir = self.fm.entries[idx]
            icon, display = self.fm.get_display(name)
            line = f" {icon} {display}"
            
            if idx == self.fm.selected_idx:
                stdscr.addstr(2 + i, 0, line.ljust(w - 1), curses.A_REVERSE)
            else:
                stdscr.addstr(2 + i, 0, line)
        
        status = f" Chars: {self.char_map} | Loop: {'Y' if self.loop else 'N'} | Smooth: {'Y' if self.smooth else 'N'} | FPS: {self.fps} "
        stdscr.addstr(h - 2, 0, status.ljust(w), curses.A_DIM)
        
        controls = " ↑↓:Nav  Enter:Play  Space:Play  B:Stop  U:URL  Q:Quit  1-0:CharSet  G:Gray  N:Newlines  A:AutoExit  F:FrameSkip  W:Wide  L:Loop  S:Smooth  T:Stretch  ?:Help "
        stdscr.addstr(h - 1, 0, controls[:w - 1], curses.A_DIM)
        
        # Only show help overlay when toggled on (not always)
        if self.show_help and h > 20 and w > 40:
            overlay_w = 36
            overlay_h = 14
            start_y = (h - overlay_h) // 2
            start_x = (w - overlay_w) // 2
            
            # Draw box border
            for i in range(overlay_h):
                stdscr.addstr(start_y + i, start_x, " " * overlay_w, curses.A_REVERSE)
            
            help_lines = [
                "    CONTROLS    ",
                "────────────────────────",
                " ↑↓ Navigate",
                " Enter/Space Play",
                " B Stop  U Enter URL",
                " Streams: rtsp/rtmp/udp/srt",
                " 1-0 Charset (9,0=Emoji)",
                " G Gray  N Newlines",
                " A AutoExit  F FrameSkip",
                " W WideMode  S Smooth",
                " T Stretch  L Loop",
                " +/- FPS  ? Help  Q Quit",
            ]
            
            for i, line in enumerate(help_lines):
                if i == 0:
                    stdscr.addstr(start_y + i, start_x + (overlay_w - len(line)) // 2, line, curses.A_BOLD)
                else:
                    stdscr.addstr(start_y + i, start_x + 2, line)
        
        stdscr.refresh()
    
    def _draw_player(self, stdscr, h, w):
        stdscr.erase()
        # When playing, tplay handles everything - just show minimal info
        # and wait for stop command
        stdscr.refresh()
    
    def _handle_browser_key(self, key, stdscr, h):
        if key == ord('q'):
            return
        elif key == ord('u') or key == ord('U'):
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(h-2, 0, "Enter URL/Stream: ")
            stdscr.clrtoeol()
            stdscr.refresh()
            url = ""
            ch = 0
            pos = 15
            while ch != 10:
                ch = stdscr.getch()
                if ch == 27:
                    url = ""
                    break
                elif ch in (curses.KEY_BACKSPACE, 127, 8) and len(url) > 0:
                    url = url[:-1]
                    pos -= 1
                    stdscr.addstr(h-2, pos, " ")
                    stdscr.move(h-2, pos)
                elif 32 <= ch <= 126:
                    url += chr(ch)
                    stdscr.addstr(h-2, pos, chr(ch))
                    pos += 1
                stdscr.clrtoeol()
                stdscr.refresh()
            curses.curs_set(0)
            curses.noecho()
            if url and is_playable(url):
                self.current_file = url
                self._start_play(url)
            return
        elif key == ord(' '):
            self._play_selected()
        elif key == curses.KEY_UP:
            self.fm.move_up()
        elif key == curses.KEY_DOWN:
            self.fm.move_down()
        elif key in (curses.KEY_BACKSPACE, 127, 27):
            self.fm.go_parent()
        elif key in (ord('\n'), ord('\r')):
            result = self.fm.open_selected()
            if result and is_playable(result):
                self.current_file = result
                self._start_play(result)
        elif key == ord('.'):
            self.fm.hidden = not self.fm.hidden
            self.fm.reload()
        elif key == ord('?') or key == ord('/'):
            self.show_help = not self.show_help
        elif key in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'), ord('0')):
            self.char_map = CHAR_MAPS[chr(key)]
            # Set w_mod to 2 for emoji charsets (9, 0)
            if chr(key) in ('9', '0'):
                self.w_mod = 2
            else:
                self.w_mod = 1
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('g') or key == ord('G'):
            self.gray = not self.gray
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('t') or key == ord('T'):
            self.stretch = not self.stretch
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('n') or key == ord('N'):
            self.new_lines = not self.new_lines
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('a') or key == ord('A'):
            self.auto_exit = not self.auto_exit
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('f') or key == ord('F'):
            self.frame_skip = not self.frame_skip
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('w') or key == ord('W'):
            self.w_mod = 2 if self.w_mod == 1 else 1
            if self.playing and self.player.is_running():
                self.player.stop()
                self._start_play(self.current_file)
        elif key == ord('l') or key == ord('L'):
            self.loop = not self.loop
        elif key == ord('s') or key == ord('S'):
            self.smooth = not self.smooth
        elif key == ord('+'):
            self.fps = min(60, self.fps + 5)
        elif key == ord('-'):
            self.fps = max(10, self.fps - 5)

    def _handle_player_key(self, key):
        if key == ord('b'):
            self.player.stop()
            self.playing = False
            self.current_file = None
            self._cleanup_terminal()
        elif key == ord(' '):
            self.player.stop()
            self.playing = False
            self._cleanup_terminal()
        elif key == ord('l') or key == ord('L'):
            self.loop = not self.loop
        elif key == ord('s') or key == ord('S'):
            self.smooth = not self.smooth
        elif key == ord('+'):
            self.fps = min(60, self.fps + 5)
        elif key == ord('-'):
            self.fps = max(10, self.fps - 5)
    
    def _play_selected(self):
        if self.fm.selected_entry:
            if is_playable(self.fm.selected_entry):
                self.current_file = self.fm.selected_entry
                self._start_play(self.fm.selected_entry)
    
    def _start_play(self, filepath):
        self.player.play(
            filepath, self.char_map, self.loop, self.smooth, self.fps,
            self.gray, self.stretch, self.auto_exit, self.new_lines, self.frame_skip, self.w_mod
        )
        self.playing = True


def main():
    start_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~')
    
    if not os.path.exists(start_path):
        start_path = os.path.expanduser('~')
    
    app = TPlayApp(start_path)
    app.run()


if __name__ == '__main__':
    main()