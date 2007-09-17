from baseaction import BaseAction

class DBRecorder(BaseAction):
    """
    This action takes a dictionary of music data and inserts it into the database
    """
    def process(self, file):
        from masterapp import model
        record = model.Music()
        for key in file.keys():
            try:
                setattr(record, key, file[key])
            except:
                pass #This just means the database doesn't store that piece of info
        model.Session.save(record)
        model.Session.commit()
        file["id"] = record.id
        return file
