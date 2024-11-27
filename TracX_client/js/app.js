const canvas = document.getElementById("visualizationCanvas");
const ctx = canvas.getContext("2d");

const connections = [
    // Nose, eyes, ears
    [0, 1], [0, 2], [1, 2], [1, 3], [2, 4],
    [3, 5], [4, 6], [5, 7], [6, 8],
    // Torso
    [5, 6], [7, 9], [8, 10],
    [5, 11], [6, 12], [11, 19], [19, 12],
    [5, 18], [6, 18], [18, 17], [17, 0],
    // Legs
    [11, 13], [12, 14], [13, 15], [14, 16],
    // Feet
    [15, 24], [24, 20], [24, 22],
    [16, 25], [25, 21], [25, 23],
];

function combineKeypoints(x, y, scores) {
    const keypoints = [];
    for (let i = 0; i < x.length; i++) {
        if (x[i] !== null && y[i] !== null && scores[i] !== null) {
            keypoints.push({ x: x[i], y: y[i], score: scores[i] });
        } else {
            keypoints.push({ x: 0, y: 0, score: 0 });
        }
    }
    return keypoints;
}

function drawStickFigure(keypoints, imageSize) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Set canvas aspect ratio based on image size, keeping max height fixed
    const aspectRatio = imageSize[1] / imageSize[0];
    canvas.width = canvas.height * aspectRatio;

    // Scale factor for canvas
    const xScale = canvas.width / imageSize[1];
    const yScale = canvas.height / imageSize[0];

    keypoints.forEach((person) => {
        // Combine x, y, and score into a single keypoint array
        const personKeypoints = combineKeypoints(person.x, person.y, person.score);

        // Extract valid keypoints (score > 0.3)
        const validPoints = personKeypoints.filter((kp) => kp.score > 0.3);

        // Draw joints
        validPoints.forEach((kp) => {
            const x = kp.x * xScale;
            const y = kp.y * yScale;
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();
        });

        // Draw connections
        connections.forEach(([start, end]) => {
            const startPoint = personKeypoints[start];
            const endPoint = personKeypoints[end];
            if (
                startPoint &&
                endPoint &&
                startPoint.score > 0.3 &&
                endPoint.score > 0.3
            ) {
                ctx.beginPath();
                ctx.moveTo(startPoint.x * xScale, startPoint.y * yScale);
                ctx.lineTo(endPoint.x * xScale, endPoint.y * yScale);
                ctx.strokeStyle = "blue";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        });
    });
}

// WebSocket connection setup
const websocket = new WebSocket("ws://localhost:8765");

websocket.onopen = () => {
    console.log("WebSocket connection established.");
};

websocket.onmessage = (event) => {
    const message = event.data;

    function parseJSON(text) {
        text = text.replace(/NaN/g, "null");
        return JSON.parse(text);
    }

    // Check if the message is a Blob
    if (message instanceof Blob) {
        // Read the Blob as text
        message.text().then((text) => {
            try {
                const data = parseJSON(text); // Parse the JSON
                const keypoints = data.keypoints;
                const metadata = data.metadata;
                const imageSize = metadata.image_size;

                drawStickFigure(keypoints, imageSize);
            } catch (error) {
                console.error("Failed to parse JSON:", error);
            }
        }).catch((error) => {
            console.error("Failed to read Blob:", error);
        });
    } else {
        // Handle cases where the message is already a string
        try {
            const data = parseJSON(message); // Parse the JSON
            const keypoints = data.keypoints;
            const metadata = data.metadata;
            const imageSize = metadata.image_size;

            drawStickFigure(keypoints, imageSize);
        } catch (error) {
            console.error("Failed to parse JSON:", error);
        }
    }
};

websocket.onclose = () => {
    console.log("WebSocket connection closed.");
};

websocket.onerror = (error) => {
    console.error("WebSocket error:", error);
};
