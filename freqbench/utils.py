import os

# Context manager to suppress stderr output
class SuppressStderr:
    def __enter__(self):
        self.null_fd = os.open(os.devnull, os.O_RDWR)
        self.stderr = os.dup(2)
        os.dup2(self.null_fd, 2)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.dup2(self.stderr, 2)
        os.close(self.null_fd)
