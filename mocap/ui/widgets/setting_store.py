

class Info_storage():
    def __init__(self):
        self.settings = {
            'video_list':[],
            'calibration':'',
            'config': "Config.toml",
            'rotate': False,
            'pose2d':'',
            'openSim': True,
            'blender': False,
            'others':{},
        }

    def update(self,name,value):
        if not name in self.settings:
            print('Illeagale setting')
            raise ValueError(name)
        self.settings[name] = value

    def read(self):
        return self.settings