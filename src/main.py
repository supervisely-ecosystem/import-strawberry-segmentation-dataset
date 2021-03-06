
import zipfile, os
import supervisely as sly
import sly_globals as g
from supervisely.io.fs import get_file_name
import gdown, glob


def create_ann(masks_folder):
    labels = []
    mask_pathes = [os.path.join(masks_folder, curr_mask) for curr_mask in os.listdir(masks_folder)]

    for mask in mask_pathes:
        ann_np = sly.imaging.image.read(mask)[:, :, 0]
        if not ann_np.any():
            continue
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

    items_path = os.path.join(g.work_dir_path, g.work_dir)
    items_names = os.listdir(items_path)

    new_project = api.project.create(g.WORKSPACE_ID, g.project_name, change_name_if_conflict=True)
    api.project.update_meta(new_project.id, g.meta.to_json())

    new_dataset = api.dataset.create(new_project.id, g.dataset_name, change_name_if_conflict=True)

    img_fine = os.path.join(items_path, "*", g.images_folder, "*")
    img_pathes = glob.glob(img_fine)
    img_pathes.sort()
    img_names = [sly.io.fs.get_file_name_with_ext(img_path) for img_path in img_pathes]

    masks_fine = os.path.join(items_path, "*", g.anns_folder)
    masks_folders = glob.glob(masks_fine)
    masks_folders.sort()

    progress = sly.Progress('Upload items', len(items_names), app_logger)

    for i in range(0, len(img_pathes), g.batch_size):
        curr_img_pathes = img_pathes[i : i + g.batch_size]
        curr_img_names = img_names[i : i + g.batch_size]
        curr_masks_folders = masks_folders[i : i + g.batch_size]

        annotations = [create_ann(masks_folder) for masks_folder in curr_masks_folders]

        img_infos = api.image.upload_paths(new_dataset.id, curr_img_names, curr_img_pathes)
        img_ids = [im_info.id for im_info in img_infos]
        api.annotation.upload_anns(img_ids, annotations)

        progress.iters_done_report(g.batch_size)

    g.my_app.stop()


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": g.TEAM_ID,
        "WORKSPACE_ID": g.WORKSPACE_ID
    })
    g.my_app.run(initial_events=[{"command": "import_strawberry"}])


if __name__ == '__main__':
    sly.main_wrapper("main", main)