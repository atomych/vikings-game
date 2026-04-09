class FrameSequence:
    def __init__(self, animation_name, frames_number: int, frame_duration, loop=True):
        self.animation_name = animation_name
        self.frames_number = frames_number

        self.frame_duration = frame_duration
        self.current_frame_index = 0
        self.elapsed_time: float = 0.0
        self.is_playing = False
        self.loop = loop

    def update(self, dt):
        if not self.is_playing:
            return
        self.elapsed_time += dt
        if self.elapsed_time >= self.frame_duration:
            self.elapsed_time -= self.frame_duration
            self.current_frame_index += 1

            if self.current_frame_index >= self.frames_number:
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index -= 1
                    self.is_playing = False

    def get_frame(self) -> int:
        return self.current_frame_index

    def run(self):
        self.is_playing = True
        self.current_frame_index = 0
        self.elapsed_time = 0.0

    def stop(self):
        self.is_playing = False
        self.current_frame_index = 0
        self.elapsed_time = 0.0

    def pause(self):
        self.is_playing = False




