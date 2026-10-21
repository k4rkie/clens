# Clens

Clens is a semantic image seach tool that allows users 
to index a given directory of images and search through it 
using natural language, search for matching images using 
another image etc. locally on their device.

## Installation
***Still in work***

## Usage

1.  Start the clens server
```bash
clens server start
```

2. Index a directory
```bash
clens index ./Images
```
This may take a few moments depending upon on the number of images in the given directory.

3. Find an image
```bash
clens find "image of a dog"
```
