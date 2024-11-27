import argparse
import asyncio
import json
import logging

import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import websockets


class SimpleRenderer:
    def __init__(self):
        """
        Initialize the stick figure visualizer.
        """
        self.fig, self.ax = plt.subplots()
        self.skeleton_lines = None
        self.keypoints = None
        plt.ion()  # Turn on interactive mode

        # Connect the close event
        self.fig.canvas.mpl_connect("close_event", self.handle_close)

    def init(self):
        """
        Set up the matplotlib plot for the stick figure.
        """
        self.ax.set_aspect("equal")
        self.ax.grid(True)
        self.ax.set_title("TracX Visualization Demo")
        self.ax.invert_yaxis()

    def handle_close(self, event):
        """
        Handle the plot window close event.
        """
        logging.info("Plot window closed. Stopping WebSocket client...")
        asyncio.get_event_loop().stop()  # Stop the asyncio event loop

    def render(self, keypoints, skeleton, image_size, kpt_thr=0.3):
        """
        Render the stick figure visualization.

        Args:
            keypoints (np.ndarray): The keypoints for each person in the frame. Shape: (N, K, 3).
            skeleton (list): The skeleton connections for drawing lines between keypoints.
            image_size (tuple): The size of the image frame.
        """
        # Clear the previous plot
        self.ax.clear()

        self.ax.set_xlim(0, image_size[1])
        self.ax.set_ylim(image_size[0], 0)

        # Extract coordinates and scores
        x = keypoints[:, :, 0]  # Shape (N, K)
        y = keypoints[:, :, 1]  # Shape (N, K)
        scores = keypoints[:, :, 2]  # Shape (N, K)

        # Mask valid keypoints across all people (N, K)
        valid_mask = scores > kpt_thr

        # Draw all joints for all people
        self.ax.scatter(x[valid_mask], y[valid_mask], c="r", s=50, zorder=5)

        # Draw skeleton links
        for i, j in skeleton:  # Iterate over joint pairs
            # Only consider valid keypoints for both joints in the pair
            valid_links = valid_mask[:, i] & valid_mask[:, j]

            # Coordinates for valid links
            x_start = x[:, i][valid_links]
            y_start = y[:, i][valid_links]
            x_end = x[:, j][valid_links]
            y_end = y[:, j][valid_links]

            # Plot the skeleton links for valid keypoints
            self.ax.plot(
                np.stack([x_start, x_end], axis=0),
                np.stack([y_start, y_end], axis=0),
                "b",
                zorder=1,
            )

    def update(self, data: str):
        """
        Update the plot with new motion data.

        Args:
            data (str): Raw JSON-encoded motion data.
        """
        try:
            # Load JSON data
            data = json.loads(data)

            # Parse keypoints and metadata
            keypoints = data["keypoints"]
            image_size = tuple(data["metadata"]["image_size"])

            # Group keypoints by person
            # NOTE: Perhaps this should be done on the server side
            x = np.array([kp["x"] for kp in keypoints])  # (N, K)
            y = np.array([kp["y"] for kp in keypoints])  # (N, K)
            scores = np.array([kp["score"] for kp in keypoints])  # (N, K)
            keypoints = np.stack([x, y, scores], axis=-1)  # (N, K, 3)  # (N, K, 3)
            keypoints = np.nan_to_num(keypoints, nan=0.0)
            keypoints = np.where(keypoints == None, 0.0, keypoints)

            # TODO: Server should send skeleton information
            # skeleton = data["metadata"].get("skeleton", [])  # Skeleton information for drawing connections
            skeleton = [
                # nose, eyes, ears
                (0, 1),
                (0, 2),
                (1, 2),
                (1, 3),
                (2, 4),
                (3, 5),
                (4, 6),
                (5, 7),
                (6, 8),
                # torso
                (5, 6),
                (7, 9),
                (8, 10),
                (5, 11),
                (6, 12),
                (11, 19),
                (19, 12),
                (5, 18),
                (6, 18),
                (18, 17),
                (17, 0),
                # legs
                (11, 13),
                (12, 14),
                (13, 15),
                (14, 16),
                # feet
                (15, 24),
                (24, 20),
                (24, 22),
                (16, 25),
                (25, 21),
                (25, 23),
            ]

            # Render the frame
            self.render(keypoints, skeleton, image_size)

            # Update the plot
            self.fig.canvas.flush_events()
            plt.pause(0.01)
        except Exception as e:
            logging.error(
                "Invalid data received. Check server output or consult the documentation."
            )

            import traceback

            logging.debug(traceback.format_exc())


async def websockets_client(host: str, port: int):
    """
    WebSocket client to receive motion data and visualize it.

    Args:
        host (str): The WebSocket server host.
        port (int): The WebSocket server port.
    """
    try:
        # Create a renderer instance
        renderer = SimpleRenderer()

        # Connect to the WebSocket server
        async with websockets.connect(f"ws://{host}:{port}") as websocket:
            while True:  # Keep the connection open
                renderer.update(await websocket.recv())
    except ConnectionRefusedError:
        logging.error(
            f"Host unreachable at {args.host}:{args.port}. Please ensure the server is running and try again."
        )
    except websockets.ConnectionClosed as e:
        logging.error(f"Connection closed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

        import traceback

        logging.debug(traceback.format_exc())


def main(args):
    """
    Run asyncio event loop alongside Matplotlib visualization.
    """
    # Configure logging
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO if not args.debug else logging.DEBUG,
    )

    # Set matplotlib logger to INFO
    mpl_logger = logging.getLogger("matplotlib")
    mpl_logger.setLevel(logging.INFO)

    # Run the client
    client = websockets_client(args.host, args.port)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TracX WebSocket Client")
    parser.add_argument(
        "--host", type=str, default="localhost", help="WebSocket server host."
    )
    parser.add_argument("--port", type=int, default=8765, help="WebSocket server port.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()
    main(args)
