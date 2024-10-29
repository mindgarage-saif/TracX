from .base import BaseSkeleton


class TheiaSkeleton(BaseSkeleton):
    def __init__(self):
        joint_names = [
            "Pelvis",  # 0
            "RThigh",  # 1
            "RLeg",  # 2
            "RFoot",  # 3
            "LThigh",  # 4
            "LLeg",  # 5
            "LFoot",  # 6
            "Thorax",  # 7
            "RArm",  # 8
            "RForearm",  # 9
            "RHand",  # 10
            "LArm",  # 11
            "LForearm",  # 12
            "LHand",  # 13
            "Head",  # 14
        ]
        connections = {
            ("Pelvis", "RThigh"),
            ("Pelvis", "LThigh"),
            ("Pelvis", "Thorax"),
            ("RThigh", "RLeg"),
            ("RLeg", "RFoot"),
            ("LThigh", "LLeg"),
            ("LLeg", "LFoot"),
            ("Thorax", "RArm"),
            ("RArm", "RForearm"),
            ("RForearm", "RHand"),
            ("Thorax", "LArm"),
            ("LArm", "LForearm"),
            ("LForearm", "LHand"),
            ("Thorax", "Head"),
        }
        # rotations = {
        #     0: "Pelvis_wrt_Lab",
        #     3: "RFoot_wrt_Lab",
        #     6: "LFoot_wrt_Lab",
        #     "1-2": "RThigh_wrt_Lab",
        #     "2-3": "RLeg_wrt_Lab",
        #     "4-5": "LThigh_wrt_Lab",
        #     "5-6": "LLeg_wrt_Lab",
        #     7: "Thorax_wrt_Lab",
        #     "8-9": "RArm_wrt_Lab",
        #     "9-10": "RForearm_wrt_Lab",
        #     10: "RHand_wrt_Lab",
        #     "11-12": "LArm_wrt_Lab",
        #     "12-13": "LForearm_wrt_Lab",
        #     13: "LHand_wrt_Lab",
        #     14: "Head_wrt_Lab",
        # }
        super().__init__(joint_names, connections)
        self.set_feet_joints(
            [
                "RFoot",
                "LFoot",
            ],
        )
