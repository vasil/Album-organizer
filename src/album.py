import os
import logging
import pyexiv2
import datetime

BIRTH_DATETIME = datetime.datetime(2010, 8, 15)
DEST_DIRNAME = '/mnt/Public/Shared Pictures/Nana.ORG/'
ORIG_DIRNAME = '/mnt/Public/Shared Pictures/Nana/'
FILENAME_FORMAT = 'NANA_%Y%m%dT%H%M%S'
DATETIME_EXIF = 'Exif.Image.DateTime'


def _configure_logger():
    LOG_FILENAME = os.path.join('..', 'log', 'album.log')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=LOG_FILENAME)


def get_newname(filename, after_date=BIRTH_DATETIME):
    image_metadata = pyexiv2.Image(filename)
    image_metadata.readMetadata()
    image_datetime = image_metadata[DATETIME_EXIF]
    week = ((image_datetime - after_date).days / 7) + 1
    assert week > 0, 'Image taken before %s.' % BIRTH_DATETIME
    filename = image_datetime.strftime(FILENAME_FORMAT)
    return (week, filename)


def create_dest_directory(dest_dirname):
    if not os.path.isdir(dest_dirname):
        logging.info('Creating destination directory %s.' % dest_dirname)
        os.mkdir(dest_dirname)


def check_and_create(week):
    week_pathname = os.path.join(DEST_DIRNAME, week)
    if not os.path.isdir(week_pathname):
        logging.info('Creating directory %s.' % week_pathname)
        os.mkdir(week_pathname)
    return week_pathname


def dir_traverse(dirname):
    logging.info("Starting to organize images from %s." % dirname)
    for root, dirs, files in os.walk(dirname, topdown=True):
        for file in files:
            try:
                old_filename = os.path.join(root, file)
                (week, new_filename) = get_newname(old_filename)
                extension = os.path.splitext(old_filename)[1].lower()
                week_pathname = check_and_create('week%s' % week)
                new_filename = os.path.join(week_pathname,
                                            new_filename + extension)
                if not os.path.exists(new_filename):
                    os.rename(old_filename, new_filename)
                    logging.debug("%s goes in %s" % (old_filename,
                                                     new_filename))
                else:
                    logging.warning("%s already exists." % new_filename)
            except Exception, e1:
                # Gotta catch em all. Pokemon!
                logging.error('Error while processing %s -- %s.' % (
                    old_filename,
                    e1))


def main():
    _configure_logger()
    create_dest_directory(DEST_DIRNAME)
    dir_traverse(ORIG_DIRNAME)

if __name__ == '__main__':
    main()
