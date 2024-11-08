# MBPR: Multi_Body_Pose_Reconstruction
English | [简体中文](README_CN.md)

**Paper**：Real-time simulation reconstruction of pedestrian emergency posture in collision accident from monocular images

# 1.Shoulders Of Giants：

[1] [SMPL](https://smpl.is.tue.mpg.de/)：A parameterized human body model

[2] [SPIN](https://www.seas.upenn.edu/~nkolot/projects/spin/)：3D human reconstruction method

[3] [human_model_viewer](https://github.com/Lemon-XQ/human_model_viewer)：Visual adjustment of SMPL parameters 

[4] [SMPL_Tools](https://github.com/wmj142326/SMPL_Tools)：This is based on [human_model_viewer](https://github.com/Lemon-XQ/human_model_viewer), we developed a target [SMPL](https://smpl.is.tue.mpg.de/)annotation tool

# 2.Pipline

<img src="README.assets/Fig1.png" style="zoom: 40%;" />

# 3.Tutorial

0. Download：`git clone https://github.com/wmj142326/MBPR`

1. Environment configuration:[SPIN/README.md](https://github.com/wmj142326/MBPR/tree/master/SPIN#readme)

2. Run`estimation.py`

   ```python
   python estimation.py --checkpoint=data/model_checkpoint.pt --img_file=input_img/01 --outfile=out/01
   ```
   
   > `input_img/01` is a folder to store input images
   > 
   > `out/01` is a folder to store the output results，include：pic_outfile, pic_outfile_shape, pkl_outfile

3. copy folders：

   madymo/images == input_img/01;

   madymo/pkl_file == out/pkl_outfile;


4. Run `ped_pkl2xml.py`：

   ```python
   python ped_pkl2xml.py
   ```

5. The output is saved in a folder：`madymo/xml_file/`

6.  Visualization：Import `madymo/xml_file/*.xml`into MADYMO software for viewing.

# 4.Appendix

In `madymo/mesh/` folder，we provided the SMPL `.obj` results, Visualization by [SMPL_Tools](https://github.com/wmj142326/SMPL_Tools)， need`.pkl` to `.ini`：
   ```python
python ped_pkl2ini.py
   ```
# 5. Citation
   ```python
@ARTICLE{10746249,
  author={Wang, MeiJun and Meng, Yu and Xu, Yan and Li, Quan and Nie, Bingbing},
  journal={IEEE Transactions on Intelligent Transportation Systems}, 
  title={Real-Time Reconstruction of Multi-Body Pedestrian Pre-Impact Posture in Collision Accidents From Monocular Images}, 
  year={2024},
  volume={},
  number={},
  pages={1-15},
  keywords={Pedestrians;Accidents;Injuries;Image reconstruction;Videos;Three-dimensional displays;Pose estimation;Computational modeling;Shape;Real-time systems;Pre-impact posture;pose reconstruction;multi-body pedestrian model;SMPL model;reconstruction of pedestrian-vehicle collision},
  doi={10.1109/TITS.2024.3486214}}
   ```