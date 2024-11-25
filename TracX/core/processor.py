import logging
from collections import deque

from PyQt6.QtCore import QMutex, QObject, QThread, QWaitCondition, pyqtSignal

from TracX.recording.video_player import VideoPlayer


class VideoProcessor(QObject):
    frame = pyqtSignal(object)

    def __init__(self, player: VideoPlayer):
        super().__init__()
        logging.info("Creating video processor %d for player %d", id(self), id(player))
        self._player: VideoPlayer = player
        self._player.frame.connect(self._enqueue_frame)

        # Processing flag and buffer queue
        self.is_running = False
        self.is_paused = False
        self.frame_queue = deque()
        self.queue_mutex = QMutex()
        self.queue_not_empty = QWaitCondition()

        # Default processing function: return the same frame
        self.process = lambda frame: frame

        # Processing thread
        self._thread = QThread(self)
        self._thread.run = self._process_frames

        self.moveToThread(self._thread)
        self.start()

    def _enqueue_frame(self, frame):
        """Add a new frame to the queue for processing, if not paused."""
        if self.is_running and not self.is_paused:
            logging.debug(
                "Procssor %d received a new frame (%d queued)",
                id(self),
                len(self.frame_queue),
            )
            self.queue_mutex.lock()
            self.frame_queue.append(frame)
            self.queue_not_empty.wakeAll()  # Signal the processing thread if it’s waiting
            self.queue_mutex.unlock()

        else:
            logging.warning(
                "Processor %d is paused or stopped, frame will be emitted directly",
                id(self),
            )
            self.frame.emit(frame)

    def _process_frames(self):
        """Process frames in the queue sequentially."""
        while self.is_running:
            self.queue_mutex.lock()
            while not self.frame_queue and self.is_running:
                self.queue_not_empty.wait(self.queue_mutex)  # Wait for new frames

            if not self.is_running:  # Stop processing if the processor is shutting down
                self.queue_mutex.unlock()
                break

            frame = self.frame_queue.popleft() if self.frame_queue else None
            self.queue_mutex.unlock()

            if frame is not None:
                # Process the frame
                processed_frame = self.process(frame)
                self.frame.emit(processed_frame)

    def stop(self):
        """Stop processing, drop all frames, and reset the processor."""
        logging.info("Stopping video processor %d", id(self))
        logging.debug(
            "%d unprocessed frames still in queue will be dropped",
            len(self.frame_queue),
        )
        self.queue_mutex.lock()
        self.is_running = False
        self.is_paused = False
        self.frame_queue.clear()  # Drop all pending frames
        self.queue_not_empty.wakeAll()  # Wake the thread if it’s waiting
        self.queue_mutex.unlock()

        logging.debug("Waiting for the processing thread to finish...")
        if self._thread.isRunning():
            self._thread.quit()
            self._thread.wait()

        logging.debug("Video processor %d stopped", id(self))

    def pause(self):
        """Pause processing and drop all unprocessed frames."""
        logging.info("Pausing video processor %d", id(self))
        self.queue_mutex.lock()
        self.is_paused = True
        self.frame_queue.clear()  # Drop all pending frames
        self.queue_mutex.unlock()

    def resume(self):
        """Resume processing if it was paused."""
        if self.is_running and self.is_paused:
            logging.info("Resuming paused video processor %d", id(self))
            self.queue_mutex.lock()
            self.is_paused = False
            self.queue_not_empty.wakeAll()  # Wake the processing thread if it’s waiting
            self.queue_mutex.unlock()

    def start(self):
        """Start or resume processing."""
        if (
            not self._thread.isRunning()
        ):  # Start from scratch if the thread was never started or stopped
            logging.info("Starting video processor %d", id(self))
            self.is_running = True
            self.is_paused = False
            self._thread.start()
        elif self.is_paused:  # Resume if it was paused
            self.resume()
