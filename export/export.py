"""
export/export.py

Utilities to export simulation results and animation media.

Features
- Export time-series kinematics to CSV (uses pandas)
- Save Matplotlib figures to PNG
- Create GIF animations from a sequence of image frames (uses imageio or Pillow)
- Create MP4 videos using imageio/ffmpeg when available or matplotlib FFMpegWriter

The exporter does not perform kinematic calculations — it expects the
caller (GUI/animation) to provide numeric data and rendered frames.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional
import os
import warnings

import numpy as np

try:
    import pandas as pd
except Exception:  # pragma: no cover - handled at runtime
    pd = None

try:
    import imageio
except Exception:
    imageio = None

try:
    from PIL import Image
except Exception:
    Image = None

from matplotlib.figure import Figure


class Exporter:
    """Exporter helper for simulation results and media.

    Methods are static and accept data/frames produced by the simulation
    and GUI. They raise informative errors when optional dependencies are
    missing.
    """

    @staticmethod
    def export_time_series_csv(path: str, t: Iterable[float], data: Dict[str, Iterable[float]]) -> None:
        """Export time-series data to CSV.

        Parameters
        ----------
        path : str
            Output CSV file path.
        t : iterable
            Time vector.
        data : dict
            Dictionary mapping column names to iterables of the same length
            as `t` (e.g., 'theta2', 'theta3', 'omega2', ...).
        """

        if pd is None:
            raise RuntimeError("Pandas is required to export CSV. Please install pandas.")

        df = pd.DataFrame({"time": np.asarray(list(t), dtype=float)})
        for k, v in data.items():
            df[k] = np.asarray(list(v), dtype=float)

        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        df.to_csv(path, index=False)

    @staticmethod
    def export_png(path: str, fig: Figure, dpi: int = 150) -> None:
        """Save a Matplotlib `Figure` to PNG.

        Parameters
        ----------
        path : str
            Output PNG path.
        fig : matplotlib.figure.Figure
            Figure to save.
        dpi : int
            Dots-per-inch.
        """

        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        fig.savefig(path, dpi=dpi)

    @staticmethod
    def export_gif(path: str, frames: List[np.ndarray], fps: int = 20) -> None:
        """Create a GIF from a list of image frames (numpy arrays or PIL Images).

        Parameters
        ----------
        path : str
            Output GIF path.
        frames : list
            Sequence of frames. Each frame may be a HxWx3 uint8 numpy array
            or a PIL Image.
        fps : int
            Frames per second.
        """

        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        if imageio is not None:
            # imageio expects frames as arrays or PIL images
            try:
                duration = 1.0 / float(max(1, fps))
                imageio.mimsave(path, frames, format="GIF", duration=duration)
                return
            except Exception as exc:  # fallback to Pillow
                warnings.warn(f"imageio GIF save failed: {exc}. Trying Pillow fallback.")

        if Image is not None:
            pil_frames = []
            for f in frames:
                if isinstance(f, Image.Image):
                    pil_frames.append(f.convert("RGBA"))
                else:
                    arr = np.asarray(f)
                    pil_frames.append(Image.fromarray(arr.astype("uint8")))

            if not pil_frames:
                raise RuntimeError("No frames supplied for GIF export.")

            pil_frames[0].save(path, save_all=True, append_images=pil_frames[1:], loop=0, duration=int(1000.0 / max(1, fps)))
            return

        raise RuntimeError("Cannot save GIF: install imageio or Pillow (PIL).")

    @staticmethod
    def export_mp4(path: str, frames: List[np.ndarray], fps: int = 30) -> None:
        """Create an MP4 video from frames.

        Tries imageio (ffmpeg backend) first. If not available, attempts
        to use matplotlib.animation with FFMpegWriter (requires ffmpeg).
        """

        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        if imageio is not None:
            try:
                writer = imageio.get_writer(path, fps=fps)
                for f in frames:
                    writer.append_data(np.asarray(f).astype("uint8"))
                writer.close()
                return
            except Exception as exc:
                warnings.warn(f"imageio MP4 write failed: {exc}")

        # Fallback using matplotlib's FFMpegWriter
        try:
            from matplotlib.animation import FFMpegWriter
            import matplotlib.pyplot as plt

            metadata = dict(artist="4-Bar Simulator")
            writer = FFMpegWriter(fps=fps, metadata=metadata)

            fig = plt.figure()
            ax = fig.add_subplot(111)
            im = None

            with writer.saving(fig, path, dpi=150):
                for f in frames:
                    ax.clear()
                    arr = np.asarray(f).astype("uint8")
                    ax.imshow(arr)
                    ax.axis("off")
                    writer.grab_frame()

            plt.close(fig)
            return
        except Exception as exc:
            raise RuntimeError("Cannot write MP4: install imageio with ffmpeg or ensure ffmpeg is available for matplotlib.")
