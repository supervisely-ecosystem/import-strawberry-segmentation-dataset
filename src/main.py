
import zipfile, os
import supervisely as sly
import sly_globals as g
from supervisely.io.fs import get_file_name
import gdown


def create_ann(masks_folder):
    labels = []
    mask_pathes = [os.path.join(masks_folder, curr_mask) for curr_mask in os.listdir(masks_folder)]

    for mask in mask_pathes:
        ann_np = sly.imaging.image.read(mask)[:, :, 0]
        ann_bool = ann_np == 255

        bitmap = sly.Bitmap(ann_bool)
        label = sly.Label(bitmap, g.obj_class)
        labels.append(label)

    return sly.Annotation(img_size=ann_np.shape, labels=labels)


def extract_zip():
    if zipfile.is_zipfile(g.archive_path):
        with zipfile.ZipFile(g.archive_path, 'r') as archive:
            archive.extractall(g.work_dir_path)
    else:
        g.logger.warn('Archive cannot be unpacked {}'.format(g.arch_name))
        g.my_app.stop()


@g.my_app.callback("import_strawberry")
@sly.timeit
def import_strawberry(api: sly.Api, task_id, context, state, app_logger):

    gdown.download(g.strawberry_url, g.archive_path, quiet=False)
    extract_zip()

    items_names = os.listdir(os.path.join(g.work_dir_path, g.work_dir))
    g.logger.warn('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1', items_names[0])
    new_project = api.project.create(g.WORKSPACE_ID, g.project_name, change_name_if_conflict=True)
    api.project.update_meta(new_project.id, g.meta.to_json())

    new_dataset = api.dataset.create(new_project.id, g.dataset_name, change_name_if_conflict=True)

    progress = sly.Progress('Upload items', len(items_names), app_logger)

    for curr_item_names in sly.batched(items_names, batch_size=g.batch_size):
        g.logger.warn('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1', curr_item_names[0])
        img_folders = [os.path.join(g.work_dir_path, g.work_dir, curr_item_name, g.images_folder) for curr_item_name in curr_item_names]
        g.logger.warn('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1', img_folders[0])
        img_pathes = [os.path.join(img_folder, os.listdir(img_folder)[0]) for img_folder in img_folders]
        img_names = [sly.io.fs.get_file_name_with_ext(img_path) for img_path in img_pathes]

        masks_folders = [os.path.join(g.work_dir_path, curr_item_name, g.anns_folder) for curr_item_name in curr_item_names]
        annotations = [create_ann(masks_folder) for masks_folder in masks_folders]
        progress.iters_done_report(len(curr_item_names))

        img_infos = api.image.upload_paths(new_dataset.id, img_names, img_pathes)
        img_ids = [im_info.id for im_info in img_infos]
        api.annotation.upload_anns(img_ids, annotations)

    g.my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": g.TEAM_ID,
        "WORKSPACE_ID": g.WORKSPACE_ID
    })
    g.my_app.run(initial_events=[{"command": "import_strawberry"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)