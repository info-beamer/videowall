import sys
import time
import json
import traceback
from itertools import cycle
from threading import Thread
from ibquery import InfoBeamerQuery, InfoBeamerQueryException

class Client(Thread):
    def __init__(self, addr):
        super(Client, self).__init__()
        self._addr = addr
        self._state = "disconnected"
        self.daemon = True
        self.start()

    def run(self):
        while 1:
            try:
                self.reconnect()
            except InfoBeamerQueryException:
                time.sleep(0.2)
                continue

            try:
                while 1:
                    line = self._io.readline().strip()
                    if not line:
                        break
                    self._state = line
            except KeyboardInterrupt:
                break
            except Exception:
                print "something went wrong. reconnecting"
                self._state = "disconnected"
                traceback.print_exc()
                time.sleep(1)

    def reconnect(self):
        self._io = InfoBeamerQuery(self._addr).node("videowall").io(raw=True)

    def send(self, **data):
        self._io.write(json.dumps(data) + "\n")
        self._io.flush()
        self._state = "waiting for confirmation"

    @property
    def state(self):
        return self._state

def main(playlist_filename, display_addrs):
    playlist = [videos.strip().split(",") for videos in file(playlist_filename)]

    for line, videos in enumerate(playlist):
        if len(videos) != len(display_addrs):
            print "mismatch between number of provided videos (%d) and number of screens (%d) in line %d" % (
                len(videos), len(display_addrs), line+1)
            sys.exit(1)

    next_videos = cycle(playlist).next

    clients = []
    for screen_id, addr in enumerate(display_addrs):
        print "adding screen %d at %s" % (screen_id, addr)
        clients.append(Client(addr))

    def all_in_any_of(states, *any_of):
        return all(state in any_of for state in states)

    def any_in_any_of(states, *any_of):
        return any(state in any_of for state in states)

    while 1:
        states = [client.state for client in clients]
        for addr, state in zip(display_addrs, states):
            print "%-30s %s" % (addr, repr(state))
        print

        if all_in_any_of(states, "none", "finished") or any_in_any_of(states, "error"):
            videos = next_videos()
            for video, client in zip(videos, clients):
                client.send(cmd = "load", filename = video)
        elif all_in_any_of(states, "paused"):
            for client in clients:
                client.send(cmd = "start")
        time.sleep(0.1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "%s <playlist.txt> <addr-screen-0> [<addr-screen-1> ...]" % sys.argv[0]
        sys.exit(1)
    main(sys.argv[1], sys.argv[2:])
