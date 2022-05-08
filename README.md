* Source images should be a simple object on a white background
* Driving videos should represent a similar object with either a video (MP4) or GIF

### How to generate a _FOM_ demo
Go to the **fom** directory.

Remove **fom** package prefix from:
- line 4 and 5 of `generator.py`
- line 6 of `util.py`
- line 4 of `dense_motion.py`
- line 4 of `keypoint_detector.py`

Run the next line in the terminal:

python demo.py --fps `fps` --config config/mgif-256.yaml --driving_video drv_video/`video` --source_image src_image/`image` --checkpoint checkpoints/mgif-cpk.pth.tar --result_video ../results/`result` --relative --adapt_scale

When done with directly generating a demo, re-add the **fom** package prefix, as it is needed by the scripts described below.

### How to generate a sprite sheet
Run `spritesheet-generator.py`, input a _source image_ and a _driving video_, then click on **GENERATE**

### How to create an animation
Run `cartoon-generator.py`, input one or more sentences on different lines, then click on **GENERATE**
