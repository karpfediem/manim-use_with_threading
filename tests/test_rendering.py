import multiprocessing
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from manim_use_with_threading import CreateCircle
from manim import config, tempconfig
from pathlib import Path
import pytest


def run_rendering():
    scene = CreateCircle()
    scene.render()
    assert scene.renderer.num_plays is not 0  # ! This will raise PytestUnhandledThreadExceptionWarning, check warnings
    

def rmtree(root: Path):
    if root.exists() and root.is_dir():
        for p in root.iterdir():
            if p.is_dir():
                rmtree(p)
            else:
                p.unlink()
        root.rmdir()


class TestRendering:
    tempdir = Path('temp')

    @pytest.fixture(autouse=True)
    def setup_each_test(self, request):
        """Set up the test and assert the file was rendered at the correct location (.mp4 not a single frame .png)"""
        self.tempdir.mkdir(exist_ok=True)

        test_dir = self.tempdir / request.node.name
        if test_dir.exists():
            rmtree(test_dir)
        test_dir.mkdir()

        full_output_filename = str((test_dir / 'output.mp4').absolute())
        with tempconfig({"output_file":  full_output_filename}):
            yield
            assert Path(config.output_file).exists()
            assert config.output_file == full_output_filename

    def test_scene_api_sanity_check(self):
        """This is the normal way to call the Manim scene api and runs just fine"""
        run_rendering()

    def test_scene_api_threading_nested(self):
        """
        Submits tasks to a threadpool which submit new process tasks to a process pool.

        The thread name is set when running new processes within a threadpool.
        This fails since the threads are not named MainThread.
        """
        process_pool = ProcessPoolExecutor()

        def run_processess():
            process_futures = {process_pool.submit(run_rendering) for _ in range(1, 2)}
            for _ in as_completed(process_futures):
                pass

        with ThreadPoolExecutor() as thread_pool:
            thread_futures = {thread_pool.submit(run_processess) for _ in range(1, 2)}
            for _ in as_completed(thread_futures):
                pass

    def test_scene_api_threading_renamed(self):
        """This fails since the thread is not named MainThread"""
        thread = threading.Thread(name='NotMainThread', target=run_rendering)
        thread.start()
        thread.join()

    def test_scene_api_process_renamed(self):
        """This is okay since only the threadname is checked"""
        thread = multiprocessing.Process(name='NotMainThread', target=run_rendering)
        thread.start()
        thread.join()

    def test_scene_api_threading_correct_name(self):
        """This is okay since the thread name is MainThread"""
        thread = threading.Thread(name='MainThread', target=run_rendering)
        thread.start()
        thread.join()
