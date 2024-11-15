from collections import deque

from PyQt6.QtCore import QMutex, QObject, QThread, QWaitCondition, pyqtSignal

from mocap.recording.video_player import VideoPlayer


class VideoProcessor(QObject):
    frame = pyqtSignal(object)

    def __init__(self, player: VideoPlayer):
        super().__init__()
        self._player: VideoPlayer = player
        self._player.frame.connect(self._enqueue_frame)

        # Processing flag and buffer queue
        self.is_running = True
        self.frame_queue = deque()
        self.queue_mutex = QMutex()
        self.queue_not_empty = QWaitCondition()

        # Default processing function: return the same frame
        self.process = lambda frame: frame

        # Start the processing thread
        self._thread = QThread(self)
        self._thread.run = self._process_frames
        self._thread.start()

    def _enqueue_frame(self, frame):
        """Add a new frame to the queue for processing."""
        self.queue_mutex.lock()
        self.frame_queue.append(frame)
        self.queue_not_empty.wakeAll()  # Signal the processing thread if it’s waiting
        self.queue_mutex.unlock()

    def _process_frames(self):
        """Process frames in the queue sequentially."""
        while self.is_running:
            self.queue_mutex.lock()
            if not self.frame_queue:
                self.queue_not_empty.wait(self.queue_mutex)  # Wait for new frames

            if not self.is_running:  # Stop processing if the processor is shutting down
                self.queue_mutex.unlock()
                break

            frame = self.frame_queue.popleft()  # Retrieve the next frame
            self.queue_mutex.unlock()

            # Process the frame
            processed_frame = self.process(frame)
            self.frame.emit(processed_frame)

    def stop_processing(self):
        """Stop the processing thread gracefully."""
        self.queue_mutex.lock()
        self.is_running = False
        self.queue_not_empty.wakeAll()  # Wake the thread if it’s waiting
        self.queue_mutex.unlock()
        self._thread.quit()
        self._thread.wait()
