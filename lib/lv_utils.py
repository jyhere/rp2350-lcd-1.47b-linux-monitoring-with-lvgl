import lvgl as lv
import micropython
from machine import Timer


class event_loop:
    _EVENT_LOOP = None

    def __init__(self, freq=40, refresh_cb=None, exception_sink=None):
        self.delay = 5
        self.refresh_cb = refresh_cb
        self.exception_sink = exception_sink
        self.scheduled = 0
        self.max_scheduled = 5
        self.timer = Timer(-1)
        self.timer.init(mode=Timer.PERIODIC, period=self.delay, callback=self.timer_cb)
        event_loop._EVENT_LOOP = self

    @staticmethod
    def is_running():
        return event_loop._EVENT_LOOP is not None

    def timer_cb(self, t):
        lv.tick_inc(self.delay)
        if self.scheduled < self.max_scheduled:
            try:
                micropython.schedule(self.task_handler_ref, 0)
                self.scheduled += 1
            except RuntimeError:
                pass

    def task_handler_ref(self, _):
        self.task_handler(_)

    def task_handler(self, _):
        try:
            if lv._nesting.value == 0:
                lv.task_handler()
                if self.refresh_cb:
                    self.refresh_cb()
            self.scheduled -= 1
        except Exception as e:
            if self.exception_sink:
                self.exception_sink(e)

    def deinit(self):
        self.timer.deinit()
        event_loop._EVENT_LOOP = None
