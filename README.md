# Using Manim python API with threading (Minimal examples)

This is a showcase of how manim fails to render video output when used within renamed threads.

Threads can be manually renamed or automatically renamed by running ThreadPools in certain situations (such as spawning new process tasks within threads).

The tests expect the output file to stay the same as the configured file (ending in .mp4).

However when Manim detects the thread name is not equal to 'MainThread' it will put the play command into a queue, which causes manim to not render any animation.


See [scene.py](https://github.com/ManimCommunity/manim/blob/92b01ebbc603565b8a91a996fb0165e0d8f002a6/manim/scene/scene.py#L1057)
```python
if threading.current_thread().name != "MainThread":
    #...
    self.queue.put(("play", args, kwargs))
    return
```

Since the manim renderer has no configured animations (renderer.num_plays stays 0) it defaults to render the last frame as a PNG output.

# Run tests
```bash
pytest
```
