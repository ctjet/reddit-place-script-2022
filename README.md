# Mogus Tracker

Please note this is janky as balls. But it does work... When you can get it to run it will output cur.png, the current r/place board. Will also output highlight.png, overlay.png, and overlayGreen.png

## About

This is a script to read how many moguses are on r/place (<https://www.reddit.com/r/place/>).

## Features

amogus

## Tweaking

This is a bodge job of the original code, all of it was written starting at 681 in amogus.py, the "print("oof")"

mogus 1, 2, 3, and 4 are the filters that are used to look for the moguses
- 0 in the filter means background
- 1 means visor
- 2 means body
- 3 means it wont check pixel, can be either body or background

mogusLeniency describes how many non-body colors are allowed to be in the body and still be considered a mogus. Default 1

bgLeniency describes how many mogus body colors are allowed to be in the background and still consider it a mogus. Default 1

The filter checks:
- visor is all the same color and not the color of the body
- background and body are not the same color
- mogus body contains no more than mogusLeniency other colors
- background contains no more than bgLeniency mogus (or if it does must be part of a different mogus)
- mogus not part of another mogus

## Requirements

-   [Latest Version of Python 3](https://www.python.org/downloads/)

## Get Started

Move the file 'config_example.json' to config.json

Edit the values to replace with actual credentials and values

Note: Please use https://jsonlint.com/ to check that your JSON file is correctly formatted

```json
{
	//Where the image's path is
	"image_path": "image.png",
	// [x,y] where you want the top left pixel of the local image to be drawn on canvas
	"image_start_coords": [741, 610],
	// delay between starting threads (can be 0)
	"thread_delay": 2,
	// array of accounts to use
	"workers": {
		// username of account 1
		"worker1username": {
			// password of account 1
			"password": "password",
			// which pixel of the image to draw first
			"start_coords": [0, 0]
		},
		// username of account 2
		"worker1username": {
			// password of account 2
			"password": "password",
			// which pixel of the image to draw first
			"start_coords": [0, 0]
		}
		// etc... add as many accounts as you want (but reddit may detect you the more you add)
	}
}
```

### Notes

-   Use `.png` if you wish to make use of transparency or non rectangular images
-   If you use 2 factor authentication (2FA) in your account, then change `password` to `password:XXXXXX` where `XXXXXX` is your 2FA code.

## Run the Script

### Windows

```shell
startmogus.bat
```

**You can get more logs (`DEBUG`) by running the script with `-d` flag:**

`python3 main.py -d` or `python3 main.py --debug`