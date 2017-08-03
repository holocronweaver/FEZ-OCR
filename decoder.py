import cv2
import numpy as np
import detector
import sys
import os

# Check if passed arguments are correct.
if len(sys.argv) != 3 \
   or not os.path.exists(sys.argv[1]) or not sys.argv[2].isdigit():
    print("Usage: classifer.py <filename> <size>")
    sys.exit(0)

# Load training data and response.
samples = np.loadtxt('training.data', np.float32)
responses = np.loadtxt('responses.data', np.float32)

# Train our model.
model = cv2.ml.KNearest_create()
model.train(samples, cv2.ml.ROW_SAMPLE, responses)

# Load image and find all the glyphs.
sample_im = cv2.imread(sys.argv[1])
size = int(sys.argv[2])
boxes, thresh = detector.find_boxes(sample_im, size)

letters = []
for x1, y1, x2, y2 in boxes:
    # Cut off glyph, resize and analyse with our model.
    piece = cv2.resize(thresh[y1:y2, x1:x2], (10, 10)).reshape((1, 100))
    result, _, _, dist = model.findNearest(np.float32(piece), k=1)

    # Get rid of bad guesses.
    if dist[0][0] > 1E6:
        continue

    # Get the character and position.
    char = chr(int(result))
    center = ((x1 + x2) / 2 - 7, (y1 + y2) / 2 + 5)
    center = (int(center[0]), int(center[1]))

    # Draw letter on the image.
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(sample_im, char, center, font, 0.7, (255, 255, 255), 5)
    cv2.putText(sample_im, char, center, font, 0.7, (0, 128, 0), 2)

    # Save letter for later.
    letters.append((char, x1 * 1E5 - y1))

# Sort letters in order (top to bottom, right to left).
letters = sorted(letters, key=lambda l: l[1], reverse=True)

# Construct sentence, trying to guess where spaces.
sentence = ""
prev = 0
for l, c in letters:
    if prev - c > size * 1.5:
        sentence += ' '
    sentence += l
    prev = c

# Print sentence and display image.
print(sentence)
cv2.imshow('Decoded', sample_im)
cv2.waitKey()
cv2.destroyWindow('Decoded')
