import asyncio
import json
import logging
from typing import Any

import numpy as np
import websockets


class MotionDataStreamer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize the WebSocket server for streaming motion data.
        :param host: The host address for the WebSocket server.
        :param port: The port number for the WebSocket server.
        """
        self.host = host
        self.port = port
        self.clients = set()  # Track connected clients
        self.is_running = False

    async def _handler(self, websocket):
        """
        Handle new WebSocket connections.
        :param websocket: The WebSocket connection object.
        """
        # Add client to the connected set
        self.clients.add(websocket)
        try:
            async for _ in websocket:  # Keep the connection open
                pass
        except websockets.ConnectionClosed as e:
            logging.debug(f"Connection closed: {e}")
            exit()
        except Exception as e:
            logging.error(f"Error in handler: {e}")
            exit()
        finally:
            # Remove client on disconnect
            self.clients.remove(websocket)

    async def _broadcast(self, message: str):
        """
        Send a message to all connected clients.
        :param message: The JSON-encoded message to send.
        """
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def start_server(self):
        """
        Start the WebSocket server.
        """
        self.is_running = True
        async with websockets.serve(self._handler, self.host, self.port):
            await asyncio.Future()  # Run forever

    def start(self):
        """
        Run the WebSocket server in an asyncio event loop.
        """
        if not self.is_running:
            asyncio.run(self.start_server())

    def stop(self):
        """
        Stop the WebSocket server.
        """
        self.is_running = False

    async def stream_frame(self, data: Any):
        """
        Stream a single frame to all connected clients.
        :param data: A dictionary containing motion data to stream.
        """
        if not self.is_running:
            raise RuntimeError("The server is not running.")

        # Handle numpy arrays in the data
        def default_serializer(obj):
            if isinstance(obj, np.ndarray):
                obj = np.where(np.isnan(obj), None, obj)
                return obj.tolist()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        message = json.dumps(data, default=default_serializer).encode("utf-8")
        await self._broadcast(message)
