## What is this?

This is a window tiler, written in Python using Xlib so it (should) work 
with any window manager. I make no promises, though, as I've only tried it
with Cinnamon. 

## Why does it exist?

I like the nice things about Cinnamon but prefer window tiling that is
automatic. 

## What does it do?

Right now, this is all it does:


* Enables a three-column layout with 33/33/33, favoring a large window in the
  center and row-tile layouts on the sides, alternating left and right; when the
  display is > 1920 in width (i.e on a very large display) 
* Uses a two-column layout with 66/33 favoring the left-size as one window and
  then tiling on the right in rows. 
* Re-tiles anytime a window is created, destroyed, or its visibility is changed
* Re-arranges all the desktops when XRandR events are detected so that it can 
  re-tile according to the new space

## Should I use this?

Probably not currently, but if you are brave then feel free. It is horribly
unoptimized but it works for my use right now and it's the first time I've 
ever used Xlib. This is what you get for two hours of hacking...

## Things to do ... 

* Clean up layout abstraction (really hacky currently...) 
* Support per-virtual desktop layouts
* Add configuration options (right now some hard-coded things like
  layout-per-resolution) 
* Allow for gaps (so you can see your pretty desktop background sometimes!)


## Contributing

If you want to contribute, feel free to open a pull request
