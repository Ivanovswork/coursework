from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def create_and_upload_file(content):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    my_file = drive.CreateFile()
    my_file.SetContentFile(content)
    my_file.Upload()
    permission = my_file.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'})

    link = my_file["alternateLink"]
    print(link)
    return link


def main():
    print(create_and_upload_file())


if __name__ == '__main__':
    main()
