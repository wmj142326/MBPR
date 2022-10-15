"""
Demo code

To run our method, you need a bounding box around the person. The person needs to be centered inside the bounding box and the bounding box should be relatively tight. You can either supply the bounding box directly or provide an [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) detection file. In the latter case we infer the bounding box from the detections.

In summary, we provide 3 different ways to use our demo code and models:
1. Provide only an input image (using ```--img```), in which case it is assumed that it is already cropped with the person centered in the image.
2. Provide an input image as before, together with the OpenPose detection .json (using ```--openpose```). Our code will use the detections to compute the bounding box and crop the image.
3. Provide an image and a bounding box (using ```--bbox```). The expected format for the json file can be seen in ```examples/im1010_bbox.json```.

Example with OpenPose detection .json
```
python3 estimation.py --checkpoint=data/model_checkpoint.pt --img_file=input_img --openpose_file=input_openpose --outfile=out
```
Example with predefined Bounding Box
```
python3 estimation.py --checkpoint=data/model_checkpoint.pt --img_file=input_img --bbox_file=input_bbox --outfile=out
```
Example with cropped and centered image
```
python3 estimation.py --checkpoint=data/model_checkpoint.pt --img_file=input_img --outfile=out
python3 estimation.py --checkpoint=data/model_checkpoint.pt --img_file=input_img/01 --outfile=out/01

```

Running the previous command will save the results in ```examples/im1010_{shape,shape_side}.png```. The file ```im1010_shape.png``` shows the overlayed reconstruction of human shape. We also render a side view, saved in ```im1010_shape_side.png```.
"""
import time

import torch
from torchvision.transforms import Normalize
import numpy as np
import cv2
import argparse
import json
import os
import joblib
from tqdm import tqdm

from models import hmr, smpl
from utils.imutils import crop
from utils.renderer import Renderer
# from utils.demo_utils import convert_crop_cam_to_orig_img
import config
import constants
import os

parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint', required=True, help='Path to pretrained checkpoint')
parser.add_argument('--img_file', type=str, required=True, help='Path to input image')
parser.add_argument('--bbox_file', type=str, default=None,
                    help='Path to .json file containing bounding box coordinates')
parser.add_argument('--openpose_file', type=str, default=None, help='Path to .json containing openpose detections')
parser.add_argument('--outfile', type=str, default=None,
                    help='Filename of output images. If not set use input filename.')


def create_file_path(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def bbox_from_openpose(openpose_file, rescale=1.2, detection_thresh=0.2):
    """Get center and scale for bounding box from openpose detections."""
    with open(openpose_file, 'r') as f:
        keypoints = json.load(f)['people'][0]['pose_keypoints_2d']
    keypoints = np.reshape(np.array(keypoints), (-1, 3))
    valid = keypoints[:, -1] > detection_thresh
    valid_keypoints = keypoints[valid][:, :-1]
    center = valid_keypoints.mean(axis=0)
    bbox_size = (valid_keypoints.max(axis=0) - valid_keypoints.min(axis=0)).max()
    # adjust bounding box tightness
    scale = bbox_size / 200.0
    scale *= rescale
    return center, scale


def bbox_from_json(bbox_file):
    """Get center and scale of bounding box from bounding box annotations.
    The expected format is [top_left(x), top_left(y), width, height].
    """
    with open(bbox_file, 'r') as f:
        bbox = np.array(json.load(f)['bbox']).astype(np.float32)
    ul_corner = bbox[:2]
    center = ul_corner + 0.5 * bbox[2:]
    width = max(bbox[2], bbox[3])
    scale = width / 200.0
    # make sure the bounding box is rectangular
    return center, scale


def process_image(img_file, bbox_file, openpose_file, input_res=224):
    """Read image, do preprocessing and possibly crop it according to the bounding box.
    If there are bounding box annotations, use them to crop the image.
    If no bounding box is specified but openpose detections are available, use them to get the bounding box.
    """
    normalize_img = Normalize(mean=constants.IMG_NORM_MEAN, std=constants.IMG_NORM_STD)
    img = cv2.imread(img_file)[:, :, ::-1].copy()  # PyTorch does not support negative stride at the moment
    if bbox_file is None and openpose_file is None:
        # Assume that the person is centerered in the image
        height = img.shape[0]
        width = img.shape[1]
        center = np.array([width // 2, height // 2])
        scale = max(height, width) / 200
    else:
        if bbox_file is not None:
            center, scale = bbox_from_json(bbox_file)
        elif openpose_file is not None:
            center, scale = bbox_from_openpose(openpose_file)
    img = crop(img, center, scale, (input_res, input_res))
    img = img.astype(np.float32) / 255.
    img = torch.from_numpy(img).permute(2, 0, 1)
    norm_img = normalize_img(img.clone())[None]
    return img, norm_img


if __name__ == '__main__':
    args = parser.parse_args()
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    # import torch.backends.cudnn as cudnn
    # cudnn.benchmark = True

    # Load pretrained model
    model = hmr.hmr(config.SMPL_MEAN_PARAMS).to(device)
    checkpoint = torch.load(args.checkpoint)
    model.load_state_dict(checkpoint['model'], strict=False)

    # Load SMPL model
    smpl = smpl.SMPL(config.SMPL_MODEL_DIR,
                batch_size=1,
                create_transl=False).to(device)
    model.eval()

    # Setup renderer for visualization
    renderer = Renderer(focal_length=constants.FOCAL_LENGTH, img_res=constants.IMG_RES, faces=smpl.faces)

    # Preprocess input image and generate predictions
    for img_name in (os.listdir(args.img_file)):
        t0 = time.time()

        if args.bbox_file is not None:
            bbox_name = img_name.split('.')[0] + '_bbox.json'
            bbox_path = os.path.join(args.bbox_file, bbox_name)
        else:
            bbox_path = args.bbox_file

        if args.openpose_file is not None:
            openpose_name = img_name.split('.')[0] + '_openpose.json'
            openpose_path = os.path.join(args.openpose_file, openpose_name)
        else:
            openpose_path = args.openpose_file

        img_path = os.path.join(args.img_file, img_name)
        img, norm_img = process_image(img_path, bbox_path, openpose_path, input_res=constants.IMG_RES)
        with torch.no_grad():
            pred_rotmat, pred_betas, pred_camera = model(norm_img.to(device))
            pred_output = smpl(betas=pred_betas, body_pose=pred_rotmat[:, 1:],
                               global_orient=pred_rotmat[:, 0].unsqueeze(1), pose2rot=False)
            pred_vertices = pred_output.vertices
            pred_pose = pred_output.body_pose
            pred_joints3d = pred_output.joints
            global_orient = pred_output.global_orient

        # Calculate camera parameters for rendering
        camera_translation = torch.stack([pred_camera[:, 1], pred_camera[:, 2],
                                          2 * constants.FOCAL_LENGTH / (constants.IMG_RES * pred_camera[:, 0] + 1e-9)],
                                         dim=-1)
        camera_translation = camera_translation[0].cpu().numpy()
        pred_vertices = pred_vertices[0].cpu().numpy()
        img = img.permute(1, 2, 0).cpu().numpy()

        # Render parametric shape
        img_shape = renderer(pred_vertices, camera_translation, img)

        # Render side views
        aroundy = cv2.Rodrigues(np.array([0, np.radians(90.), 0]))[0]
        center = pred_vertices.mean(axis=0)
        rot_vertices = np.dot((pred_vertices - center), aroundy) + center

        # Render non-parametric shape
        img_shape_side = renderer(rot_vertices, camera_translation, np.ones_like(img))

        pic_outfile = os.path.join(args.outfile, 'pic_outfile/')
        create_file_path(pic_outfile)
        pic_outfile_shape = os.path.join(args.outfile, 'pic_outfile_shape/')
        create_file_path(pic_outfile_shape)

        # pic_outfile = args.outfile+'/pic_outfile'

        # save reconstructions
        shape_name = img_name.split('.')[0] + '_shape.png'
        shape_side_name = img_name.split('.')[0] + '_shape_side.png'
        shape_outfile = pic_outfile + shape_name
        shape_side_outfile = pic_outfile_shape + shape_side_name
        cv2.imwrite(shape_outfile, 255 * img_shape[:, :, ::-1])
        cv2.imwrite(shape_side_outfile, 255 * img_shape_side[:, :, ::-1])

        # Save results to a pickle file
        pred_camera = pred_camera.cpu().numpy()
        pred_pose = pred_pose.cpu().numpy()
        pred_betas = pred_betas.cpu().numpy()
        pred_joints3d = pred_joints3d.cpu().numpy()
        global_orient = global_orient.cpu().numpy()

        output_dict = {
            'pred_camera': pred_camera,
            'verts': pred_vertices,
            'pose': pred_pose,
            'beats': pred_betas,
            'joints3d': pred_joints3d,
            'global_orient': global_orient
        }
        output_result = {}
        output_result[0] = output_dict
        pkl_name = img_name.split('.')[0] + '.pkl'
        pkl_outfile = os.path.join(args.outfile, 'pkl_outfile/')
        create_file_path(pkl_outfile)
        model_outfile = pkl_outfile + pkl_name

        # pkl_outfile = args.outfile + '/model_outfile'

        joblib.dump(output_result, model_outfile)

        t1 = time.time()

        print(img_name, t1 - t0)
