"""July 2023: This code is written by Jameel Malik. Some conversion functions are adopted from https://github.com/otaheri/MANO
This code implements 2D hand pose fitting using a PyTorch based Forward kinematics hand skeleton layer (axis angles representation is used).
Create virtual env e.g., using conda, install PyTorch, and other dependencies using pip install..
Note: initial 3D reference pose of hand is provided to the layer as input, see 'HandSkeletonLayer' function.
"""

import json
import os
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
import toml
import torch
import torch.nn.functional as F


def to_tensor(array, dtype=torch.float32):
    """Converts a numpy array to a PyTorch tensor.

    Parameters
    ----------
    - array: numpy array to be converted
    - dtype: desired data type of the tensor (default: torch.float32)

    Returns
    -------
    - tensor: PyTorch tensor

    """
    return torch.tensor(array, dtype=dtype)


def computeP(calib_file, undistort=False):
    """Compute projection matrices from toml calibration file.

    INPUT:
    - calib_file: calibration .toml file.
    - undistort: boolean

    OUTPUT:
    - P: projection matrix as list of arrays
    """
    calib = toml.load(calib_file)

    P = []
    for cam in list(calib.keys()):
        print(cam)
        if cam != "metadata":
            K = np.array(calib[cam]["matrix"])
            if undistort:
                S = np.array(calib[cam]["size"])
                dist = np.array(calib[cam]["distortions"])
                optim_K = cv2.getOptimalNewCameraMatrix(
                    K,
                    dist,
                    [int(s) for s in S],
                    1,
                    [int(s) for s in S],
                )[0]
                Kh = np.block([optim_K, np.zeros(3).reshape(3, 1)])
            else:
                Kh = np.block([K, np.zeros(3).reshape(3, 1)])
            R, _ = cv2.Rodrigues(np.array(calib[cam]["rotation"]))
            T = np.array(calib[cam]["translation"])
            H = np.block([[R, T.reshape(3, 1)], [np.zeros(3), 1]])

            P.append(Kh @ H)

    return P


def createDic(list):
    new_dict = {}
    for i in range(len(list)):
        new_dict[list[i]] = i
    return new_dict


def readTrc(path_to_3d_joints):
    # path_to_3d_joints = os.path.expanduser('~/miniconda3/envs/Pose2Sim/lib/python3.8/site-packages/Pose2Sim/ROM2_RTMPose/3c/28983_29913_23138/pose-3d/ROM2_RTMPose_0-3038_filt_butterworth.trc')
    with open(path_to_3d_joints) as trc_file:
        lines = trc_file.readlines()
        joints = []
        joint_names = lines[3].split("\t")[2:]  # remove empty string
        elem = joint_names[-1]
        elem2 = joint_names[1]
        for line in lines[5:]:
            joint = line.replace("\n", "").split("\t")[2:]
            xs = np.array(joint[::3], dtype=np.float64)
            ys = np.array(joint[1::3], dtype=np.float64)
            zs = np.array(joint[2::3], dtype=np.float64)
            joints.append([[z, x, y] for x, y, z in zip(xs, ys, zs)])
        joint_names.remove(elem2)
        new_joint_names = list(filter((elem2).__ne__, joint_names))
        new_joint_names = list(filter((elem).__ne__, new_joint_names))
        joint_to_idx = createDic(new_joint_names)
    return np.array(joints, dtype=np.float64), joint_to_idx


def BodySkeletionLayer(pose, transl, Projection_mat, img_size, J, j_to_idx):
    """Implements the PyTorch based forward kinematics function of hand skeleton that allows automatic gradient computation.
    The joint order is from https://github.com/otaheri/MANO/blob/master/mano/joints_info.py
    Update this reference pose for a particular user (bonelengths will be automatically calculated from this pose).
    This 3D pose is provided in camera coordinates and in meters.
    """
    order = [
        j_to_idx["Hip"],
        j_to_idx["RHip"],
        j_to_idx["RKnee"],
        j_to_idx["RAnkle"],
        j_to_idx["RBigToe"],
        j_to_idx["RSmallToe"],
        j_to_idx["RHeel"],
        j_to_idx["LHip"],
        j_to_idx["LKnee"],
        j_to_idx["LAnkle"],
        j_to_idx["LBigToe"],
        j_to_idx["LSmallToe"],
        j_to_idx["LHeel"],  # 12
        j_to_idx["Neck"],
        j_to_idx["Head"],
        j_to_idx["Nose"],
        j_to_idx["RShoulder"],
        j_to_idx["RElbow"],
        j_to_idx["RWrist"],
        j_to_idx["LShoulder"],
        j_to_idx["LElbow"],
        j_to_idx["LWrist"],
    ]
    J = J[order]
    parents = np.array(
        [-1, 0, 1, 2, 3, 3, 3, 0, 7, 8, 9, 9, 9, 0, 13, 14, 13, 16, 17, 13, 19, 20],
    )
    J = torch.from_numpy(J)
    joints = torch.ones(1, J.size(0), J.size(1))
    joints[0, :, :] = J
    # print(joints)
    parents = to_tensor(parents).long()
    joints = torch.unsqueeze(joints, dim=-1)
    # print(joints)
    rel_joints = joints.clone()
    rel_joints[:, 1:] -= joints[:, parents[1:]]
    # print(rel_joints)
    rot_mats = batch_rodrigues(pose.view(-1, 3)).view([1, -1, 3, 3])
    transforms_mat = transform_mat(
        rot_mats.reshape(-1, 3, 3),
        rel_joints.reshape(-1, 3, 1),
    ).reshape(-1, joints.shape[1], 4, 4)
    # print(transforms_mat)
    transform_chain = [transforms_mat[:, 0]]
    # print(len(transform_chain))
    # print(transform_chain)
    # print('parent shape',parents.shape[0])
    for i in range(1, parents.shape[0]):
        # print('i',i,parents[i])
        # print(transforms_mat[:,i])
        curr_res = torch.matmul(transform_chain[parents[i]], transforms_mat[:, i])
        transform_chain.append(curr_res)
        # print('transform_chain',len(transform_chain))
    transforms = torch.stack(transform_chain, dim=1)
    posed_joints = transforms[:, :, :3, 3]
    # print(posed_joints)
    posed_joints = posed_joints + transl.unsqueeze(dim=1)
    h_keys_proj = multiview_projection_batch(Projection_mat.detach(), posed_joints)
    h_keys_proj = normalize_keys_batch(h_keys_proj, img_size[1], img_size[0])
    return posed_joints, h_keys_proj


def get_2D_joints(path_to_2d_joints, which_person=0):
    joints_2d = []
    confidences = []
    for file in sorted(
        os.listdir(path_to_2d_joints),
        key=lambda x: int(x.split("_")[1]),
    ):
        if file.endswith(".json"):
            with open(os.path.join(path_to_2d_joints, file)) as f:
                data = json.load(f)
                xs = data["people"][which_person]["pose_keypoints_2d"][::3]
                ys = data["people"][which_person]["pose_keypoints_2d"][1::3]
                confidence = data["people"][which_person]["pose_keypoints_2d"][2::3]
                confidences.append(confidence)
                joints_2d.append([[x, y] for x, y in zip(xs, ys)])
    return np.array(joints_2d, dtype=np.float64), np.array(
        confidences,
        dtype=np.float64,
    )


def main_HPE(
    path_to_2d_joints1,
    path_to_2d_joints2,
    path_to_2d_joints3,
    path_to_3d_joints,
):
    joint_name_to_idx = {
        "Nose": 0,
        "LEye": 1,
        "REye": 2,
        "LEar": 3,
        "REar": 4,
        "LShoulder": 5,
        "RShoulder": 6,
        "LElbow": 7,
        "RElbow": 8,
        "LWrist": 9,
        "RWrist": 10,
        "LHip": 11,
        "RHip": 12,
        "LKnee": 13,
        "RKnee": 14,
        "LAnkle": 15,
        "RAnkle": 16,
        "Head": 17,
        "Neck": 18,
        "Hip": 19,
        "LBigToe": 20,
        "RBigToe": 21,
        "LSmallToe": 22,
        "RSmallToe": 23,
        "LHeel": 24,
        "RHeel": 25,
    }
    P_new = computeP("./utils/Calib.toml")
    joints_gt_2D_all_view1, confidences_all_view1 = get_2D_joints(path_to_2d_joints1, 0)
    joints_gt_2D_all_view2, confidences_all_view2 = get_2D_joints(path_to_2d_joints2, 0)
    joints_gt_2D_all_view3, confidences_all_view3 = get_2D_joints(path_to_2d_joints3, 0)
    joint_gt_2d_views = np.array(
        [joints_gt_2D_all_view1, joints_gt_2D_all_view2, joints_gt_2D_all_view3],
    )
    joints_3d, joint_names_to_idx = readTrc(path_to_3d_joints)
    ordering = [
        joint_name_to_idx["Hip"],
        joint_name_to_idx["RHip"],
        joint_name_to_idx["RKnee"],
        joint_name_to_idx["RAnkle"],
        joint_name_to_idx["RBigToe"],
        joint_name_to_idx["RSmallToe"],
        joint_name_to_idx["RHeel"],
        joint_name_to_idx["LHip"],
        joint_name_to_idx["LKnee"],
        joint_name_to_idx["LAnkle"],
        joint_name_to_idx["LBigToe"],
        joint_name_to_idx["LSmallToe"],
        joint_name_to_idx["LHeel"],
        joint_name_to_idx["Neck"],
        joint_name_to_idx["Head"],
        joint_name_to_idx["Nose"],
        joint_name_to_idx["RShoulder"],
        joint_name_to_idx["RElbow"],
        joint_name_to_idx["RWrist"],
        joint_name_to_idx["LShoulder"],
        joint_name_to_idx["LElbow"],
        joint_name_to_idx["LWrist"],
    ]
    enhanced_3d_joints = []
    reprojection_error = []
    for j in range(len(joints_gt_2D_all_view1)):
        joint_gt_2D_view1 = joints_gt_2D_all_view1[j]
        confidences_view1 = confidences_all_view1[j]
        joint_gt_2D_view1 = joint_gt_2D_view1[ordering]
        confidences_view1 = confidences_view1[ordering]

        joint_gt_2D_view2 = joints_gt_2D_all_view2[j]
        confidences_view2 = confidences_all_view2[j]
        joint_gt_2D_view2 = joint_gt_2D_view2[ordering]
        confidences_view2 = confidences_view2[ordering]

        joint_gt_2D_view3 = joints_gt_2D_all_view3[j]
        confidences_view3 = confidences_all_view3[j]
        joint_gt_2D_view3 = joint_gt_2D_view3[ordering]
        confidences_view3 = confidences_view3[ordering]

        P = np.array(
            [
                [P_new[0][0], P_new[0][1], P_new[0][2]],
                [P_new[1][0], P_new[1][1], P_new[1][2]],
                [P_new[2][0], P_new[2][1], P_new[2][2]],
            ],
        )
        # P = np.array([[P_new[2][0],P_new[2][1],P_new[2][2]]])
        Ps_batch = torch.ones(1, 3, 3, 4)
        Ps_batch[:, :] = torch.tensor(P)
        joint_num = len(joint_gt_2D_view3)
        joint_gt = torch.from_numpy(
            np.array([joint_gt_2D_view1, joint_gt_2D_view2, joint_gt_2D_view3]),
        )
        # joint_gt = torch.from_numpy(np.array([joint_gt_2D_view3]))
        joint_gt = torch.unsqueeze(joint_gt, dim=0).view(1, 3, joint_num, 2)
        # print(P)
        confidences_tensor = torch.from_numpy(
            np.array([confidences_view1, confidences_view2, confidences_view3]),
        )
        # confidences_tensor = torch.from_numpy(np.array([confidences_view3]))
        confidences_tensor = torch.unsqueeze(confidences_tensor, dim=0).view(
            1,
            3,
            joint_num,
            1,
        )
        torch_identity = torch.eye(3)
        # print(confidences_tensor)
        img_size = np.array([1920, 1088])  # width, height
        # h_keys_proj_gt = multiview_projection_batch(Ps_batch.detach(), joint_gt.float())
        # print(img_size[1],img_size[0])
        h_keys_proj_gt = normalize_keys_batch(
            joint_gt.float(),
            img_size[1],
            img_size[0],
        )
        # h_keys_proj_gt = multiview_projection_batch(Ps_batch.detach(), joint_gt.float())
        # h_keys_proj_gt = normalize_keys_batch(h_keys_proj_gt, img_size[1], img_size[0])
        # get the start time
        print("joint_num", joint_num)
        st = time.time()
        vari_dict = {}
        init_transl = torch.FloatTensor([0, 0, 0])
        vari_dict["transl"] = (
            init_transl.view(1, 3).clone().detach().requires_grad_(True)
        )
        vari_dict["pose"] = torch.zeros((joint_num * 3), requires_grad=True)
        params = [
            {"params": vari_dict["pose"], "lr": 0.05},
            {"params": vari_dict["transl"], "lr": 0.05},
        ]
        optimizer = torch.optim.Adam(params=params)
        lr_scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer,
            step_size=50,
            gamma=0.1,
        )
        itr = 250
        indices = [4, 5, 10, 11, 1, 2, 7, 8]
        mult_dict = {4: 10, 5: 10, 10: 10, 11: 10, 1: 5, 2: 5, 7: 5, 8: 5}
        # change multiple the loss of the joints at index 4 5 10 11 with factor 10
        for i in range(itr):
            joints_pos, h_keys_proj = BodySkeletionLayer(
                vari_dict["pose"],
                vari_dict["transl"],
                Ps_batch,
                img_size,
                joints_3d[j],
                joint_names_to_idx,
            )
            # loss1 = (torch.mul((h_keys_proj-h_keys_proj_gt).pow(2),confidences_tensor))
            # loss1[:,:,indices,:] *= 10
            loss = (
                torch.mul((h_keys_proj - h_keys_proj_gt).pow(2), confidences_tensor)
                * torch.tensor(
                    [
                        mult_dict[i] if i in indices else 1
                        for i in range(h_keys_proj.size(2))
                    ],
                    dtype=h_keys_proj.dtype,
                    device=h_keys_proj.device,
                ).view(1, 1, -1, 1)
            ).mean()  # +0.000006*vari_dict['pose'].pow(2).mean()  # test with 2d loss
            # loss = (torch.mul((h_keys_proj-h_keys_proj_gt).pow(2),confidences_tensor)).mean()\
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            lr_scheduler.step()
            # print(loss,i)
        print(j)
        top_2d = h_keys_proj.detach().numpy()
        top_data = joints_pos.detach().numpy()
        enhanced_3d_joints.append(top_data)
        reprojection_error.append(top_2d)
        # get the end time
        et = time.time()
        # get the execution time
        elapsed_time = et - st
        print("Execution time of Body Skeleton Layer:", elapsed_time * 1000, "ms")
    enhanced_3d_joints = np.array(enhanced_3d_joints)
    reprojection_error = np.array(reprojection_error)
    np.save("enhanced_3d_joints_with_weighted_feet_and_hip.npy", enhanced_3d_joints)
    gt_joint = joints_3d
    gt_joint = torch.from_numpy(gt_joint)
    gt_joint = torch.unsqueeze(gt_joint, dim=0)
    #################################### Display Code #######################################
    x = np.zeros(joint_num)
    y = np.zeros(joint_num)
    z = np.zeros(joint_num)
    a = np.zeros(joint_num)
    b = np.zeros(joint_num)
    c = np.zeros(joint_num)
    d = np.zeros(joint_num)
    e = np.zeros(joint_num)
    f = np.zeros(joint_num)
    print("Displaying the 3D poses...")
    print(gt_joint.shape, enhanced_3d_joints.shape)
    print(reprojection_error.shape)
    print(joint_gt_2d_views.shape)
    for k in range(3):
        for i in range(joint_num):
            e[i] = reprojection_error[0, 0, k][i, 0]
            f[i] = reprojection_error[0, 0, k][i, 1]
            joint_gt = torch.from_numpy(
                np.array([joint_gt_2d_views[k, 2460][ordering]]),
            )
            joint_gt = torch.unsqueeze(joint_gt, dim=0).view(1, 1, joint_num, 2)
            joint_gt = normalize_keys_batch(joint_gt.float(), img_size[1], img_size[0])
            joint_gt = joint_gt.detach().numpy()
            # print(joint_gt.shape)
            a[i] = joint_gt[0, 0, i, 0]
            b[i] = joint_gt[0, 0, i, 1]
            joint_gt2 = torch.from_numpy(
                np.array([joint_gt_2d_views[k, 2620][ordering]]),
            )
            joint_gt2 = torch.unsqueeze(joint_gt2, dim=0).view(1, 1, joint_num, 2)
            joint_gt2 = normalize_keys_batch(
                joint_gt2.float(),
                img_size[1],
                img_size[0],
            )
            joint_gt2 = joint_gt2.detach().numpy()
            x[i] = joint_gt2[0, 0, i, 0]
            y[i] = joint_gt2[0, 0, i, 1]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for o in range(joint_num):
            ax.scatter(e[o], f[o], color="r")
            ax.scatter(a[o], b[o], color="b")
            ax.scatter(x[o], y[o], color="g")
            ax.text(e[o], f[o], "%s" % (str(o)), size=10, zorder=1, color="r")
            ax.text(a[o], b[o], "%s" % (str(o)), size=10, zorder=1, color="b")
            ax.text(x[o], y[o], "%s" % (str(o)), size=10, zorder=1, color="g")
        # ax.scatter(e, f, color='r')
        # ax.scatter(a, b, color='b')
        plt.show()
    for j in range(600):
        for i in range(joint_num):
            a[i] = gt_joint[0, j + 2460][i, 0]
            b[i] = gt_joint[0, j + 2460][i, 1]
            c[i] = gt_joint[0, j + 2460][i, 2]
            x[i] = enhanced_3d_joints[j, 0][i, 0]
            y[i] = enhanced_3d_joints[j, 0][i, 1]
            z[i] = enhanced_3d_joints[j, 0][i, 2]
            d[i] = gt_joint[0, 2620][i, 0]
            e[i] = gt_joint[0, 2620][i, 1]
            f[i] = gt_joint[0, 2620][i, 2]
        fig = plt.figure()
        ax = fig.add_subplot((111), projection="3d")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.scatter(y, x, z, color="r")
        ax.scatter(b, a, c, color="b")
        ax.scatter(e, d, f, color="g")
        # ax.scatter(f, -d, e, color='g')
        # for i in range(J):
        # ax.text(c[i], -a[i], b[i], '%s' % (str(i)), size=10, zorder=1, color='r')
        Edges = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [0, 5],
            [5, 6],
            [6, 7],
            [7, 8],
            [0, 9],
            [9, 10],
            [10, 11],
            [11, 12],
            [0, 13],
            [13, 14],
            [14, 15],
            [15, 16],
            [0, 17],
            [17, 18],
            [18, 19],
            [19, 20],
        ]
        for e in Edges:
            break
            ax.plot(z[e], -x[e], y[e], c="b")  # Reference 3D pose
            ax.plot(c[e], -a[e], b[e], c="r")  # Target 3D pose

        #'''
        # For axes equal
        max_range = np.array(
            [x.max() - x.min(), y.max() - y.min(), z.max() - z.min()],
        ).max()
        Xb = 0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][0].flatten() + 0.5 * (
            x.max() + x.min()
        )
        Yb = 0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][1].flatten() + 0.5 * (
            y.max() + y.min()
        )
        Zb = 0.5 * max_range * np.mgrid[-1:2:2, -1:2:2, -1:2:2][2].flatten() + 0.5 * (
            z.max() + z.min()
        )
        for xb, yb, zb in zip(Xb, Yb, Zb):
            ax.plot([zb], [xb], [yb], "w")
        #'''

        plt.show()


##############################################################################################
def multiview_projection_batch(Ps, points):
    """Ps (projection matrices for each view):B x n_view x 3 x 4
    points: B x n_points x 3
    returns: B x n_view x n_points x 2
    """
    # print(Ps.shape,points.shape)
    B, n_view, dim1, dim2 = Ps.shape
    _, n_p, d = points.shape
    points = points.view(B, 1, n_p, d).expand(
        -1,
        n_view,
        -1,
        -1,
    )  # B x n_views x n_points x 3
    points_homo = torch.cat((points, torch.ones(B, n_view, n_p, 1)), 3)
    proj_homo = torch.transpose(
        torch.bmm(
            Ps.reshape(-1, dim1, dim2),
            torch.transpose(points_homo.reshape(-1, n_p, d + 1), 2, 1),
        ),
        2,
        1,
    )
    proj_homo = proj_homo / (proj_homo[:, :, -1].view(B * n_view, n_p, 1))

    return proj_homo[:, :, :-1].reshape(B, n_view, n_p, 2)


def normalize_keys_batch(keys, h, w):
    """keys:Bxn_viewsxNx2"""
    keys[:, :, :, 0] /= w
    keys[:, :, :, 1] /= h
    return keys


def transform_mat(R, t):
    """Creates a batch of transformation matrices
    Args:
        - R: Bx3x3 array of a batch of rotation matrices
        - t: Bx3x1 array of a batch of translation vectors
    Returns:
        - T: Bx4x4 Transformation matrix
    """
    # No padding left or right, only add an extra row
    return torch.cat([F.pad(R, [0, 0, 0, 1]), F.pad(t, [0, 0, 0, 1], value=1)], dim=2)


def batch_rodrigues(rot_vecs, epsilon=1e-8, dtype=torch.float32):
    """Calculates the rotation matrices for a batch of rotation vectors

    Parameters
    ----------
    rot_vecs: torch.tensor Nx3
        array of N axis-angle vectors

    Returns
    -------
    R: torch.tensor Nx3x3
        The rotation matrices for the given axis-angle parameters

    """
    batch_size = rot_vecs.shape[0]
    device, dtype = rot_vecs.device, rot_vecs.dtype

    angle = torch.norm(rot_vecs + 1e-8, dim=1, keepdim=True)
    rot_dir = rot_vecs / angle

    cos = torch.unsqueeze(torch.cos(angle), dim=1)
    sin = torch.unsqueeze(torch.sin(angle), dim=1)

    # Bx1 arrays
    rx, ry, rz = torch.split(rot_dir, 1, dim=1)
    K = torch.zeros((batch_size, 3, 3), dtype=dtype, device=device)

    zeros = torch.zeros((batch_size, 1), dtype=dtype, device=device)
    K = torch.cat([zeros, -rz, ry, rz, zeros, -rx, -ry, rx, zeros], dim=1).view(
        (batch_size, 3, 3),
    )

    ident = torch.eye(3, dtype=dtype, device=device).unsqueeze(dim=0)
    return ident + sin * K + (1 - cos) * torch.bmm(K, K)


if __name__ == "__main__":
    path_to_2d_joints1 = os.path.expanduser(
        r"E:\Uni\Data\LIHS\2dFitting\RTMPOSE_L\ROM2\23087_json",
    )
    path_to_2d_joints2 = os.path.expanduser(
        r"E:\Uni\Data\LIHS\2dFitting\RTMPOSE_L\ROM2\29092_json",
    )
    path_to_2d_joints3 = os.path.expanduser(
        r"E:\Uni\Data\LIHS\2dFitting\RTMPOSE_L\ROM2\29913_json",
    )
    path_to_3d_joints = os.path.expanduser(
        r"C:\Users\Jeremias\anaconda3\envs\Pose2Sim\Lib\site-packages\Pose2Sim\RMTPoseL\RMTPoseL\ROM2\3c\23087_29092_29913\ROM2_RTMPose_0-3038_filt_butterworth.trc",
    )
    # joints_3d, joint_names_to_idx = readTrc()
    main_HPE(
        path_to_2d_joints1,
        path_to_2d_joints2,
        path_to_2d_joints3,
        path_to_3d_joints,
    )
