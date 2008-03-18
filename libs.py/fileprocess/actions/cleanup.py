from baseaction import BaseAction

log = logging.getLogger(__name__)

class Cleanup(BaseAction):
    """
    A special file action that is invoked when a file needs to be cleaned up.
    Unlike the other actions, this one doesn't return its file. This is a 
    terminal action.
    """
    def process(self, file):
        fileprocess.UploadStatus(
            file.get('msg', "File Successfully Uploaded"),
            file.get('na', fileprocess.na.NOTHING),
            file
        )

        try:
            os.remove(file['fname'])
        except:
            pass
