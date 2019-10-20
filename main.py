import sys
import io
import string
import curses
import signal


def readfile(file_name):
	stringIO = io.StringIO()
	with open(file_name,'r') as f:
		return ''.join([c for c in f.read() if c in string.printable[:-3]])

def end_game(stdscr,exit_msg=''):
	curses.echo()
	curses.nocbreak()
	stdscr.keypad(False)
	curses.endwin()
	print(exit_msg)

def handle_signals(stdscr,gs):
	def handler(signum, frame):
		end_game(stdscr,exit_msg=str(gs['pos']))
		exit(1)
	signal.signal(signal.SIGINT , handler)
	signal.signal(signal.SIGTERM, handler)

def init_curses():
	stdscr = curses.initscr()

	curses.noecho()
	curses.cbreak()
	stdscr.keypad(True)
	curses.start_color()
	curses.use_default_colors()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)

	return stdscr

def load_game_state(string,pos):
	stdscr = init_curses()

	game_state = {
		'stdscr'    : stdscr,
		'pos'       : pos,
		'text'      : string,
	}

	return game_state

def run_game(gs):
	stdscr = gs['stdscr']
	try:
		_run_game(gs)
	except Exception as e:
		end_game(stdscr,exit_msg=str(gs['pos']))
		raise e

	end_game(stdscr)

def check_bound(screen):
	height, width = screen.getmaxyx()
	y, x = screen.getyx()
	return y >= height - 1 or x >= width -1

def _run_game(gs):
	stdscr = gs['stdscr']
	stdscr.refresh()
	text = gs['text']

	draw_screen(gs['pos'],gs)

	backspace = '\x7f'
	while gs['pos'] < len(text):
		if check_bound(stdscr):
			draw_screen(gs['pos'],gs)
		key = stdscr.getkey()
		if key == text[gs['pos']]:
			stdscr.addstr(key,curses.A_UNDERLINE)
			gs['pos'] += 1
		elif key == 'KEY_RIGHT':
			stdscr.addstr(gs['text'][gs['pos']],curses.A_UNDERLINE)
			gs['pos'] += 1
		elif key != backspace:
			y, x = stdscr.getyx()
			stdscr.addstr(gs['text'][gs['pos']],curses.color_pair(1))
			stdscr.move(y,x)
			stdscr.refresh()
			while stdscr.getkey() != backspace:
				pass
			stdscr.addstr(gs['text'][gs['pos']])
			stdscr.move(y,x)
			stdscr.refresh()
		stdscr.refresh()

def draw_screen(start_pos, gs):
	screen = gs['stdscr']
	pos    = gs['pos']
	string = gs['text']
	cursor_end_pos = None
	i = start_pos
	while i < len(string):
		if check_bound(screen):
			break
		if i < pos:
			screen.addstr(string[i],curses.A_UNDERLINE)
		elif i == pos:
			cursor_end_pos = screen.getyx()
			screen.addstr(string[i])
		else:
			screen.addstr(string[i])
		i += 1
	if cursor_end_pos == None:
		raise Exception('draw_screen error, cursor_end_pos is None')
	else:
		screen.move(*cursor_end_pos)

def main(file_name,pos):
	data = readfile(file_name)
	game_state = load_game_state(data,pos)
	handle_signals(game_state['stdscr'],game_state)
	run_game(game_state)


if __name__ == '__main__':
	main(sys.argv[1],int(sys.argv[2]))
