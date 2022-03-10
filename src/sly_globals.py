
import os, sys
from pathlib import Path
import supervisely as sly


my_app = sly.AppService()
api: sly.Api = my_app.public_api

root_source_dir = str(Path(sys.argv[0]).parents[1])
sly.logger.info(f"Root source directory: {root_source_dir}")
sys.path.append(root_source_dir)

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])

logger = sly.logger

project_name = 'Strawberry'
dataset_name = 'ds'
work_dir = 'strawberry_data/strawberry'
strawberry_url = 'https://storage.googleapis.com/kaggle-data-sets/1743316/2848076/bundle/archive.zip?X-Goog-Algorithm=' \
                 'GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20220310%2' \
                 'Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20220310T132800Z&X-Goog-Expires=259199&X-Goog-SignedHeaders' \
                 '=host&X-Goog-Signature=9611a8f0daa803d197a0af226ee9444bec5bb576351a8a62b6761d7e93031959c2910c868cc52a' \
                 '861ef903a00dc575e43a964a4ce2467a15bdb77f7cbf3fe76fb2a773bdeaa66de40c3fc3d306cde900f48b10e6a1d12594322' \
                 'e1bc99588280d16590adad9d19ef0c1c1764e1bd147ab41abce119c9fbf190f9598d031e1c328091821204b16afac0ce926b7' \
                 '402091c4ab471d443c23943b4796e5a3a4b9f29778b47e070e9e658e691571517838229728d425e3fa3930e3e9f059ef56527' \
                 '73d6f53283eab7a64fd8f9e460af4337cd1bd9221b391c0f14e4d07fb3a14405400940bf47b00a6112aa81b9cf3b275bae963' \
                 '04ab773c53220ddf9860c352a966b6'

arch_name = 'archive.zip'
images_folder = 'images'
anns_folder = 'masks'
class_name = 'strawberry'

batch_size = 10

obj_class = sly.ObjClass(class_name, sly.Bitmap)
obj_class_collection = sly.ObjClassCollection([obj_class])

meta = sly.ProjectMeta(obj_classes=obj_class_collection)

storage_dir = my_app.data_dir
work_dir_path = os.path.join(storage_dir, work_dir)
sly.io.fs.mkdir(work_dir_path)
archive_path = os.path.join(work_dir_path, arch_name)
